import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from src.models import Review, ReviewStatus
from src.llm_service import llm_service
import time

logger = logging.getLogger(__name__)

class CodeAnalyzerService:
    """Service for code analysis and review"""
    
    @staticmethod
    async def analyze_code(
        session: AsyncSession,
        code: str,
        language: str,
        filename: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Review:
        """
        Analyze code and create a review record
        
        Args:
            session: Database session
            code: Code to analyze
            language: Programming language
            filename: Optional filename
            user_id: Optional user ID
            
        Returns:
            Review record with results
        """
        start_time = time.time()
        
        # Create review record
        review = Review(
            code=code,
            language=language,
            filename=filename,
            status=ReviewStatus.PROCESSING,
            user_id=user_id,
            code_lines=len(code.split('\n'))
        )
        
        session.add(review)
        await session.flush()  # Get ID without committing
        
        try:
            # Perform LLM analysis
            analysis = await llm_service.review_code(code, language, filename)
            
            # Update review with results
            review.status = ReviewStatus.COMPLETED
            review.summary = analysis.get('summary')
            review.score = analysis.get('score', 5.0)
            review.complexity = analysis.get('complexity', 5)
            review.maintainability = analysis.get('maintainability', 5.0)
            review.security_score = analysis.get('security_score', 5.0)
            review.performance_score = analysis.get('performance_score', 5.0)
            review.issues = analysis.get('issues', [])
            review.suggestions = analysis.get('suggestions', [])
            
            elapsed = time.time() - start_time
            review.processing_time = elapsed
            
            logger.info(f"Analysis completed for {filename or 'untitled'} in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            review.status = ReviewStatus.FAILED
            review.error_message = str(e)
        
        review.updated_at = datetime.utcnow()
        await session.commit()
        
        return review
    
    @staticmethod
    async def get_review(session: AsyncSession, review_id: UUID) -> Optional[Review]:
        """Get a review by ID"""
        query = select(Review).where(Review.id == review_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_reviews(
        session: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[Review]:
        """Get reviews with optional filtering"""
        query = select(Review)
        
        if user_id:
            query = query.where(Review.user_id == user_id)
        
        query = query.order_by(Review.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        return result.scalars().all()

# Singleton instance
analyzer_service = CodeAnalyzerService()
