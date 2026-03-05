"""
Seed script to populate the database with sample data
"""
from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.task_repository import TaskRepository
from app.schemas import UserCreate, TaskCreate
from datetime import datetime, timedelta

def seed_database():
    db = SessionLocal()
    user_repo = UserRepository(db)
    task_repo = TaskRepository(db)
    
    print("🌱 Seeding database...")
    
    # Create admin user
    print("Creating admin user...")
    admin_data = UserCreate(
        email="admin@taskflow.com",
        name="Admin User",
        password="admin123",
        role="administrator",
        title="System Administrator",
        isAdmin=True
    )
    
    try:
        admin = user_repo.create(admin_data)
        print(f"✅ Admin created: {admin.email}")
    except Exception as e:
        print(f"⚠️  Admin might already exist: {e}")
        admin = user_repo.get_by_email("admin@taskflow.com")
    
    # Create regular users
    users_data = [
        UserCreate(
            email="john@taskflow.com",
            name="John Doe",
            password="john123",
            role="developer",
            title="Senior Developer"
        ),
        UserCreate(
            email="jane@taskflow.com",
            name="Jane Smith",
            password="jane123",
            role="designer",
            title="UI/UX Designer"
        ),
        UserCreate(
            email="bob@taskflow.com",
            name="Bob Johnson",
            password="bob123",
            role="developer",
            title="Backend Developer"
        ),
    ]
    
    created_users = []
    for user_data in users_data:
        try:
            user = user_repo.create(user_data)
            created_users.append(user)
            print(f"✅ User created: {user.email}")
        except Exception as e:
            print(f"⚠️  User might already exist: {user_data.email}")
            user = user_repo.get_by_email(user_data.email)
            if user:
                created_users.append(user)
    
    # Create sample tasks
    print("\nCreating sample tasks...")
    
    tasks_data = [
        TaskCreate(
            title="Design new landing page",
            description="Create a modern, responsive landing page for the product",
            priority="high",
            stage="in progress",
            date=datetime.now() + timedelta(days=7),
            team=[u.id for u in created_users[:2]],
            assets=[],
            links="https://figma.com/design-link"
        ),
        TaskCreate(
            title="Implement user authentication",
            description="Add JWT-based authentication to the API",
            priority="high",
            stage="completed",
            date=datetime.now() - timedelta(days=2),
            team=[u.id for u in created_users],
            assets=[],
            links="https://github.com/project/auth"
        ),
        TaskCreate(
            title="Write API documentation",
            description="Document all API endpoints with examples",
            priority="medium",
            stage="todo",
            date=datetime.now() + timedelta(days=14),
            team=[created_users[0].id],
            assets=[],
            links=""
        ),
        TaskCreate(
            title="Fix mobile responsive issues",
            description="Address layout problems on mobile devices",
            priority="high",
            stage="in progress",
            date=datetime.now() + timedelta(days=3),
            team=[created_users[1].id],
            assets=[],
            links=""
        ),
        TaskCreate(
            title="Optimize database queries",
            description="Improve query performance and add indexes",
            priority="medium",
            stage="todo",
            date=datetime.now() + timedelta(days=10),
            team=[created_users[2].id],
            assets=[],
            links=""
        ),
        TaskCreate(
            title="Setup CI/CD pipeline",
            description="Configure automated testing and deployment",
            priority="low",
            stage="todo",
            date=datetime.now() + timedelta(days=21),
            team=[u.id for u in created_users],
            assets=[],
            links="https://github.com/project/actions"
        ),
        TaskCreate(
            title="Conduct code review",
            description="Review pull requests and provide feedback",
            priority="normal",
            stage="completed",
            date=datetime.now() - timedelta(days=1),
            team=[admin.id, created_users[0].id],
            assets=[],
            links=""
        ),
        TaskCreate(
            title="Update dependencies",
            description="Update all npm and pip packages to latest versions",
            priority="low",
            stage="todo",
            date=datetime.now() + timedelta(days=30),
            team=[created_users[2].id],
            assets=[],
            links=""
        ),
    ]
    
    for task_data in tasks_data:
        try:
            task = task_repo.create(task_data, admin.id)
            print(f"✅ Task created: {task.title}")
        except Exception as e:
            print(f"❌ Error creating task: {e}")
    
    db.close()
    print("\n✨ Database seeding completed!")
    print("\n📝 Login credentials:")
    print("   Admin: admin@taskflow.com / admin123")
    print("   User1: john@taskflow.com / john123")
    print("   User2: jane@taskflow.com / jane123")
    print("   User3: bob@taskflow.com / bob123")


if __name__ == "__main__":
    seed_database()
