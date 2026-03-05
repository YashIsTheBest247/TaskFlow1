"""Initialize database and create sample data"""
import sys
sys.path.insert(0, '.')

from app.core.database import Base, engine, SessionLocal
from app.models import *
from app.core.security import get_password_hash

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully!")

# Create sample data
db = SessionLocal()

try:
    # Create admin user
    print("\nCreating admin user...")
    from app.models.user import User
    
    admin = User(
        name="Admin User",
        email="admin@taskflow.com",
        password=get_password_hash("admin123"),
        role="administrator",
        title="System Administrator",
        isAdmin=True,
        isActive=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"✓ Admin created: {admin.email}")
    
    # Create regular users
    print("\nCreating regular users...")
    users_data = [
        ("John Doe", "john@taskflow.com", "john123", "developer", "Senior Developer"),
        ("Jane Smith", "jane@taskflow.com", "jane123", "designer", "UI/UX Designer"),
        ("Bob Johnson", "bob@taskflow.com", "bob123", "developer", "Backend Developer"),
    ]
    
    created_users = []
    for name, email, password, role, title in users_data:
        user = User(
            name=name,
            email=email,
            password=get_password_hash(password),
            role=role,
            title=title,
            isAdmin=False,
            isActive=True
        )
        db.add(user)
        created_users.append(user)
    
    db.commit()
    for user in created_users:
        db.refresh(user)
        print(f"✓ User created: {user.email}")
    
    # Create sample tasks
    print("\nCreating sample tasks...")
    from app.models.task import Task, TaskTeamMember
    from datetime import datetime, timedelta
    
    tasks_data = [
        ("Design new landing page", "high", "in progress", 7),
        ("Implement user authentication", "high", "completed", -2),
        ("Write API documentation", "medium", "todo", 14),
        ("Fix mobile responsive issues", "high", "in progress", 3),
        ("Optimize database queries", "medium", "todo", 10),
    ]
    
    for title, priority, stage, days_offset in tasks_data:
        task = Task(
            user_id=admin.id,
            title=title,
            description=f"Description for {title}",
            priority=priority,
            stage=stage,
            date=datetime.now() + timedelta(days=days_offset),
            assets=[],
            links="",
            isTrashed=False
        )
        db.add(task)
        db.flush()
        
        # Add team members
        for user in created_users[:2]:
            team_member = TaskTeamMember(task_id=task.id, user_id=user.id)
            db.add(team_member)
        
        print(f"✓ Task created: {title}")
    
    db.commit()
    
    print("\n✨ Database initialization completed!")
    print("\n📝 Login credentials:")
    print("   Admin: admin@taskflow.com / admin123")
    print("   User1: john@taskflow.com / john123")
    print("   User2: jane@taskflow.com / jane123")
    print("   User3: bob@taskflow.com / bob123")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    db.close()
