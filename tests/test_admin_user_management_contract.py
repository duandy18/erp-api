from __future__ import annotations

from app.admin.contracts.user_permission_matrix import UserPermissionMatrixOut
from app.admin.contracts.user_permission_matrix_update import UserPermissionMatrixUpdateIn
from app.iam.contracts.user_admin import UserCreateIn, UserUpdateIn


def test_user_admin_contracts_shape() -> None:
    create_body = UserCreateIn.model_validate(
        {
            "username": "operator",
            "password": "000000",
            "permission_ids": [1, 2],
            "full_name": "Operator",
            "phone": None,
            "email": None,
        }
    )
    update_body = UserUpdateIn.model_validate(
        {
            "full_name": "Operator A",
            "phone": "10086",
            "email": "operator@example.com",
            "is_active": True,
        }
    )

    assert create_body.username == "operator"
    assert create_body.permission_ids == [1, 2]
    assert update_body.is_active is True


def test_permission_matrix_contracts_shape() -> None:
    matrix = UserPermissionMatrixOut.model_validate(
        {
            "pages": [
                {
                    "page_code": "erp.system",
                    "page_name": "系统管理",
                    "sort_order": 90,
                }
            ],
            "users": [
                {
                    "user_id": 1,
                    "username": "admin",
                    "full_name": "系统管理员",
                    "is_active": True,
                    "pages": {
                        "erp.system": {
                            "read": True,
                            "write": True,
                        }
                    },
                }
            ],
        }
    )

    update_body = UserPermissionMatrixUpdateIn.model_validate(
        {
            "pages": [
                {
                    "page_code": "erp.system",
                    "can_read": True,
                    "can_write": True,
                }
            ]
        }
    )

    assert matrix.pages[0].page_code == "erp.system"
    assert matrix.users[0].pages["erp.system"].write is True
    assert update_body.pages[0].can_write is True
