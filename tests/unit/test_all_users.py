# tests/unit/test_all_users.py

import pytest
from app.authentication.controllers import get_paginated_users

@pytest.mark.asyncio
async def test_get_users_with_pagination(db_session):
    users_response = await get_paginated_users(cursor=None, limit=5, db=db_session)
    assert len(users_response.users) <= 5
    assert users_response.next_cursor is not None


@pytest.mark.asyncio
async def test_get_next_page_users(db_session):
    # First request to get the initial set of users
    first_response = await get_paginated_users(cursor=None, limit=5, db=db_session)
    cursor = first_response.next_cursor

    # Second request using the cursor to get the next set
    second_response = await get_paginated_users(cursor=cursor, limit=5, db=db_session)

    assert len(second_response.users) <= 5
    assert second_response.next_cursor is not None
