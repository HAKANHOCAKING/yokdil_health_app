"""
Security tests: Authorization, multi-tenancy, RBAC
CRITICAL: These tests ensure cross-tenant data leakage doesn't occur
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import uuid


@pytest.mark.asyncio
async def test_student_cannot_access_other_student_data(client: AsyncClient, db_session):
    """
    SECURITY TEST: Student A cannot access Student B's attempts
    """
    # Create two students in same tenant
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.core.security import get_password_hash
    
    tenant = Tenant(name="Test School")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    student_a = User(
        email="student_a@test.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Student A",
        role="student",
        tenant_id=tenant.id,
    )
    
    student_b = User(
        email="student_b@test.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Student B",
        role="student",
        tenant_id=tenant.id,
    )
    
    db_session.add(student_a)
    db_session.add(student_b)
    await db_session.commit()
    
    # Login as Student A
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "student_a@test.com", "password": "Pass123!"}
    )
    token_a = login_response.json()["access_token"]
    
    # Try to access Student B's data
    response = await client.get(
        f"/api/v1/analytics/student/{student_b.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    # Should return 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_teacher_cannot_access_other_class_data(client: AsyncClient, db_session):
    """
    SECURITY TEST: Teacher A cannot access Teacher B's class
    """
    from app.models.user import User, Class
    from app.models.tenant import Tenant
    from app.core.security import get_password_hash
    
    tenant = Tenant(name="Test School")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    teacher_a = User(
        email="teacher_a@test.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Teacher A",
        role="teacher",
        tenant_id=tenant.id,
    )
    
    teacher_b = User(
        email="teacher_b@test.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Teacher B",
        role="teacher",
        tenant_id=tenant.id,
    )
    
    db_session.add(teacher_a)
    db_session.add(teacher_b)
    await db_session.commit()
    await db_session.refresh(teacher_a)
    await db_session.refresh(teacher_b)
    
    # Create class for Teacher B
    class_b = Class(
        name="Teacher B's Class",
        teacher_id=teacher_b.id,
        tenant_id=tenant.id,
    )
    db_session.add(class_b)
    await db_session.commit()
    await db_session.refresh(class_b)
    
    # Login as Teacher A
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "teacher_a@test.com", "password": "Pass123!"}
    )
    token_a = login_response.json()["access_token"]
    
    # Try to access Teacher B's class
    response = await client.get(
        f"/api/v1/teacher/classes/{class_b.id}/students",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    
    # Should return 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_cross_tenant_data_isolation(client: AsyncClient, db_session):
    """
    SECURITY TEST: Tenant A cannot access Tenant B's data
    CRITICAL: Multi-tenancy isolation
    """
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.models.question import Question
    from app.core.security import get_password_hash
    
    # Create two tenants
    tenant_a = Tenant(name="School A")
    tenant_b = Tenant(name="School B")
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.commit()
    await db_session.refresh(tenant_a)
    await db_session.refresh(tenant_b)
    
    # Create question in Tenant B
    question_b = Question(
        tenant_id=tenant_b.id,
        exam_date="Test",
        question_no=1,
        stem_text="Test question",
        blank_position=0,
    )
    db_session.add(question_b)
    await db_session.commit()
    await db_session.refresh(question_b)
    
    # Create student in Tenant A
    student_a = User(
        email="student@tenant_a.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Student A",
        role="student",
        tenant_id=tenant_a.id,
    )
    db_session.add(student_a)
    await db_session.commit()
    
    # Login as Student A (Tenant A)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "student@tenant_a.com", "password": "Pass123!"}
    )
    token = login_response.json()["access_token"]
    
    # Try to access Question from Tenant B
    response = await client.get(
        f"/api/v1/questions/{question_b.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return 404 Not Found (question not in their tenant)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_token_reuse_detection(client: AsyncClient, db_session):
    """
    SECURITY TEST: Refresh token reuse should invalidate all tokens
    """
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.core.security import get_password_hash
    
    tenant = Tenant(name="Test School")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Test User",
        role="student",
        tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.commit()
    
    # Login and get tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Pass123!"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token once (valid)
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    
    # Try to reuse the same refresh token (SECURITY BREACH ATTEMPT)
    reuse_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    # Should return 401 and invalidate all user tokens
    assert reuse_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token reuse detected" in reuse_response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limiting_login(client: AsyncClient):
    """
    SECURITY TEST: Login endpoint should be rate limited
    """
    # Attempt multiple logins rapidly
    for i in range(10):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "WrongPass"}
        )
        
        if i >= 5:  # After 5 attempts, should be rate limited
            assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_argon2_password_hashing(db_session):
    """
    SECURITY TEST: Passwords should use Argon2id (not bcrypt)
    """
    from app.core.security import get_password_hash, verify_password
    
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    # Argon2 hashes start with $argon2id$
    assert hashed.startswith("$argon2")
    
    # Verify password works
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_admin_cannot_access_other_tenant(client: AsyncClient, db_session):
    """
    SECURITY TEST: Admin in Tenant A cannot access Tenant B's data
    Even admins are tenant-scoped
    """
    from app.models.user import User
    from app.models.tenant import Tenant
    from app.core.security import get_password_hash
    
    # Create two tenants
    tenant_a = Tenant(name="School A")
    tenant_b = Tenant(name="School B")
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.commit()
    await db_session.refresh(tenant_a)
    await db_session.refresh(tenant_b)
    
    # Create admin in Tenant A
    admin_a = User(
        email="admin@tenant_a.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Admin A",
        role="admin",
        tenant_id=tenant_a.id,
    )
    db_session.add(admin_a)
    await db_session.commit()
    
    # Create user in Tenant B
    user_b = User(
        email="user@tenant_b.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="User B",
        role="student",
        tenant_id=tenant_b.id,
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(user_b)
    
    # Login as Admin A
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tenant_a.com", "password": "Pass123!"}
    )
    token = login_response.json()["access_token"]
    
    # Try to access User B (from different tenant)
    response = await client.get(
        f"/api/v1/admin/users/{user_b.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return 403/404 (cannot access cross-tenant)
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
