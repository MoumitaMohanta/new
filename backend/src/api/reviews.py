import logging
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import json
from src.database import get_session
from src.schemas import CodeReviewRequest, CodeReviewResponse, HealthResponse
from src.code_analyzer import analyzer_service
from src.config import settings
from src.models import ReviewStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["reviews"])

@router.post("/reviews", response_model=CodeReviewResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_review(
    request: CodeReviewRequest,
    session: AsyncSession = Depends(get_session)
) -> CodeReviewResponse:
    """
    Submit code for review.
    
    Returns 202 Accepted immediately with review ID.
    Use GET /reviews/{review_id} to poll for results.
    """
    try:
        # Validate code length
        if len(request.code) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Code exceeds maximum size"
            )
        
        # Perform analysis
        review = await analyzer_service.analyze_code(
            session=session,
            code=request.code,
            language=request.language,
            filename=request.filename
        )
        
        logger.info(f"Review created: {review.id}")
        
        return CodeReviewResponse(
            id=review.id,
            status=review.status,
            created_at=review.created_at,
            updated_at=review.updated_at,
            code_lines=review.code_lines,
            processing_time=review.processing_time,
            summary=review.summary,
            score=review.score,
            issues=[],
            metrics={
                "complexity": review.complexity,
                "maintainability": review.maintainability,
                "security_score": review.security_score,
                "performance_score": review.performance_score
            },
            suggestions=review.suggestions or []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )

@router.get("/reviews/{review_id}", response_model=CodeReviewResponse)
async def get_review(
    review_id: UUID,
    session: AsyncSession = Depends(get_session)
) -> CodeReviewResponse:
    """
    Get review results by ID.
    
    Status will be:
    - pending: Review is queued
    - processing: Review is in progress
    - completed: Review finished successfully
    - failed: Review failed
    """
    review = await analyzer_service.get_review(session, review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )
    
    # Parse issues from JSON
    issues = []
    if review.issues:
        issues = review.issues if isinstance(review.issues, list) else []
    
    return CodeReviewResponse(
        id=review.id,
        status=review.status,
        created_at=review.created_at,
        updated_at=review.updated_at,
        code_lines=review.code_lines,
        processing_time=review.processing_time,
        summary=review.summary,
        score=review.score,
        issues=issues,
        metrics={
            "complexity": review.complexity,
            "maintainability": review.maintainability,
            "security_score": review.security_score,
            "performance_score": review.performance_score
        },
        suggestions=review.suggestions or []
    )

@router.get("/reviews", response_model=list[CodeReviewResponse])
async def list_reviews(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
) -> list[CodeReviewResponse]:
    """
    List recent reviews.
    
    Paginated with limit and offset.
    """
    reviews = await analyzer_service.get_reviews(
        session=session,
        limit=limit,
        offset=offset
    )
    
    return [
        CodeReviewResponse(
            id=review.id,
            status=review.status,
            created_at=review.created_at,
            updated_at=review.updated_at,
            code_lines=review.code_lines,
            processing_time=review.processing_time,
            summary=review.summary,
            score=review.score,
            issues=review.issues if isinstance(review.issues, list) else [],
            metrics={
                "complexity": review.complexity,
                "maintainability": review.maintainability,
                "security_score": review.security_score,
                "performance_score": review.performance_score
            },
            suggestions=review.suggestions or []
        )
        for review in reviews
    ]
