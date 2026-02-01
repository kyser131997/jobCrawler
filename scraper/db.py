"""
Couche de base de données SQLite pour stocker les offres d'emploi.
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_PATH

Base = declarative_base()


class Job(Base):
    """Modèle pour une offre d'emploi."""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String(500), nullable=False)
    company = Column(String(300))
    role_category = Column(String(100))  # Data Analyst, Business Analyst, Data Engineer, Other
    source = Column(String(100), nullable=False)  # Indeed, WTTJ, LinkedIn, etc.
    published_date = Column(DateTime)
    location = Column(String(300))
    url = Column(String(1000), unique=True)  # Clé unique principale
    snippet = Column(Text)  # Résumé/description courte
    detected_keywords = Column(String(500))  # Liste des mots-clés détectés (séparés par virgule)
    applied = Column(Boolean, default=False)  # Nouveau champ pour le suivi des candidatures
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'job_title': self.job_title,
            'company': self.company,
            'role_category': self.role_category,
            'source': self.source,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'location': self.location,
            'url': self.url,
            'snippet': self.snippet,
            'detected_keywords': self.detected_keywords,
            'applied': self.applied,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


class DatabaseManager:
    """Gestionnaire de base de données."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialise la connexion à la base de données."""
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Retourne une nouvelle session."""
        return self.SessionLocal()
    
    def upsert_job(self, session: Session, job_data: Dict) -> tuple[bool, bool]:
        """
        Insère ou met à jour une offre.
        
        Returns:
            (is_new, is_updated): True si nouvelle offre, True si mise à jour
        """
        url = job_data.get('url')
        
        if url:
            # Chercher par URL
            existing = session.query(Job).filter_by(url=url).first()
        else:
            # Si pas d'URL, chercher par hash (title + company + date)
            existing = session.query(Job).filter_by(
                job_title=job_data.get('job_title'),
                company=job_data.get('company'),
                published_date=job_data.get('published_date')
            ).first()
        
        if existing:
            # Toujours mettre à jour scraped_at pour la fraîcheur
            existing.scraped_at = datetime.utcnow()
            updated = True
            
            # Mise à jour des champs manquants (ex: si la date était None avant)
            for key, value in job_data.items():
                if key == 'scraped_at': continue
                if value and not getattr(existing, key):
                    setattr(existing, key, value)
                    updated = True
            return False, updated
        else:
            # Nouvelle offre
            # S'assurer que scraped_at est défini si non présent
            if 'scraped_at' not in job_data:
                job_data['scraped_at'] = datetime.utcnow()
            job = Job(**job_data)
            session.add(job)
            return True, False
    
    def bulk_upsert(self, jobs_data: List[Dict]) -> Dict[str, int]:
        """
        Insère ou met à jour plusieurs offres en masse.
        
        Returns:
            Statistiques: {'added': int, 'updated': int, 'skipped': int}
        """
        session = self.get_session()
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        try:
            for job_data in jobs_data:
                is_new, is_updated = self.upsert_job(session, job_data)
                if is_new:
                    stats['added'] += 1
                elif is_updated:
                    stats['updated'] += 1
                else:
                    stats['skipped'] += 1
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return stats
    
    def get_all_jobs(self, limit: Optional[int] = None) -> List[Dict]:
        """Récupère toutes les offres."""
        session = self.get_session()
        try:
            query = session.query(Job).order_by(Job.published_date.desc())
            if limit:
                query = query.limit(limit)
            jobs = query.all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()
            
    def update_job_status(self, job_id: int, applied: bool) -> bool:
        """Met à jour le statut de candidature d'une offre."""
        session = self.get_session()
        try:
            job = session.query(Job).filter_by(id=job_id).first()
            if job:
                job.applied = applied
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict:
        """Calcule les statistiques sur les offres."""
        session = self.get_session()
        try:
            # Total
            total = session.query(func.count(Job.id)).scalar()
            
            # Par catégorie
            by_category = session.query(
                Job.role_category,
                func.count(Job.id)
            ).group_by(Job.role_category).all()
            
            # Par source
            by_source = session.query(
                Job.source,
                func.count(Job.id)
            ).group_by(Job.source).all()
            
            # Par jour (published_date)
            by_day = session.query(
                func.date(Job.published_date),
                func.count(Job.id)
            ).group_by(func.date(Job.published_date)).all()
            
            # Top localisations
            top_locations = session.query(
                Job.location,
                func.count(Job.id)
            ).filter(Job.location.isnot(None)).group_by(Job.location).order_by(
                func.count(Job.id).desc()
            ).limit(10).all()
            
            return {
                'total': total,
                'by_category': dict(by_category),
                'by_source': dict(by_source),
                'by_day': [(str(day), count) for day, count in by_day if day],
                'top_locations': dict(top_locations)
            }
        finally:
            session.close()
    
    def clear_all(self):
        """Supprime toutes les offres (pour tests)."""
        session = self.get_session()
        try:
            session.query(Job).delete()
            session.commit()
        finally:
            session.close()
