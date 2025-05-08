from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from config.db import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    tweetId = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # relationship to tweets
    tweet = relationship("Tweet", back_populates="likes")