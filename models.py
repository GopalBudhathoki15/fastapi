from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Book(Base):
    __tablename__ = 'books'

    id:Mapped[int]  = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()