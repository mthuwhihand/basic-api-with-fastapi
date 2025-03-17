from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Request, status
from app.core.api_response import create_api_response
from app.models.users import User, UserRefreshTokens
from app.schemas.users import SignUp, SignIn, TokenPair, UserSchema, UserUpdateSchema
from app.utils import extentions
from app.utils.logger import logger
from app.core.config import (
    AccountStatuses,
    Roles,
    TokenStatuses,
    sendmail_config,
    settings,
)
from app.core.database import db
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")


def register(user_data: SignUp):
    try:
        # Check email
        existing_email = (
            db.query(User)
            .filter_by(email=user_data.email)
            .filter(User.status != AccountStatuses.DELETED.value)
            .first()
        )
        if existing_email:
            if existing_email.status == AccountStatuses.ACTIVE.value:
                return create_api_response(
                    status=status.HTTP_409_CONFLICT,
                    message="Email aldeady registered",
                )

            if existing_email.status == AccountStatuses.SUSPENDING.value:
                return create_api_response(
                    status=status.HTTP_403_FORBIDDEN,
                    message="User with this email is suspended",
                )

        # Check phone
        existing_phone = (
            db.query(User)
            .filter_by(phone=user_data.phone)
            .filter(User.status != AccountStatuses.DELETED.value)
            .first()
        )
        if existing_phone:
            if existing_phone.status == AccountStatuses.ACTIVE.value:
                return create_api_response(
                    status=status.HTTP_409_CONFLICT,
                    message="Phone aldeady registered",
                )

            if existing_phone.status == AccountStatuses.SUSPENDING.value:
                return create_api_response(
                    status=status.HTTP_403_FORBIDDEN,
                    message="User with this phone number is suspended",
                )

        # Create new user
        new_user = User(**user_data.model_dump())
        new_user.id = extentions.gen_uuid()
        new_user.password = extentions.hash_password(new_user.password)
        new_user.role = Roles.USER.value

        # Add to DB
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return create_api_response(
            status=status.HTTP_200_OK,
            message="Register successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/register SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/register Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def login(sign_in_data: SignIn):
    try:
        existing_user = (
            db.query(User)
            .filter_by(email=sign_in_data.email)
            .filter(User.status != AccountStatuses.DELETED.value)
            .first()
        )
        if not existing_user:
            return create_api_response(
                status=status.HTTP_404_NOT_FOUND,
                message="User not found",
            )

        if existing_user.status == AccountStatuses.SUSPENDING.value:
            return create_api_response(
                status=status.HTTP_403_FORBIDDEN,
                message="User is suspended",
            )

        if not extentions.is_valid_password(
            sign_in_data.password, existing_user.password
        ):
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="Invalid password",
            )

        new_refresh_token = extentions.create_refresh_token({"id": existing_user.id})
        record = UserRefreshTokens(
            id=extentions.gen_uuid(),
            user_id=existing_user.id,
            refresh_token=new_refresh_token,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        new_access_token = extentions.create_access_token(
            {"id": existing_user.id, "access_id": record.id}
        )
        data = TokenPair(refresh_token=new_refresh_token, access_token=new_access_token)

        return {
            "status": status.HTTP_200_OK,
            "message": "Login successfully!",
            "data": data,
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/login SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/login Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def get_data(request: Request):
    try:
        id = extentions.get_id_from_request(request)

        user = (
            db.query(User)
            .filter_by(id=id)
            .filter(User.status == AccountStatuses.ACTIVE.value)
            .first()
        )

        if not user:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found by this token!",
            )

        data = UserSchema.model_validate(user)

        return {
            "status": status.HTTP_200_OK,
            "message": "Retrieved user data successfully!",
            "data": data,
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/get_data SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/get_data Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def refresh_access_token(request: Request):
    try:
        request_refresh_token = extentions.get_token(request)

        record = (
            db.query(UserRefreshTokens)
            .filter(UserRefreshTokens.refresh_token == request_refresh_token)
            .first()
        )

        if record:
            if record.status == TokenStatuses.NON_LONGER_ACTIVE.value:
                return create_api_response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    message="Refresh token is no longer active!",
                )
            else:
                current_exp = extentions.decode_token(request_refresh_token).get("exp")
                new_refresh_token = extentions.create_refresh_token(
                    data={"id": record.id}, exp=current_exp
                )

                record.refresh_token = new_refresh_token
                db.commit()
                db.refresh(record)

                new_access_token = extentions.create_access_token(
                    {"id": record.user_id, "access_id": record.id}
                )
                data = TokenPair(
                    refresh_token=new_refresh_token, access_token=new_access_token
                )
                return {
                    "status": status.HTTP_200_OK,
                    "message": "Refresh token successfully!",
                    "data": data,
                }
        else:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found by this token!",
            )
    except SQLAlchemyError as e:
        db.rollback()
        logger.info(
            "SERVICE auth/refresh_access_token SQLAlchemyError Error: " + str(e)
        )
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/refresh_access_token Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def logout(request: Request):
    try:
        # token = extentions.get_token(request)
        # id = extentions.get_id_from_request(request)
        access_id = extentions.get_field_data_from_request(request, "access_id")
        record = (
            db.query(UserRefreshTokens)
            .filter(UserRefreshTokens.id == access_id)
            .first()
        )

        if record:
            record.status = TokenStatuses.NON_LONGER_ACTIVE.value
            db.commit()
            db.refresh(record)

            return create_api_response(
                status=status.HTTP_200_OK,
                message="Logged out successfully!",
            )

        else:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found by this token!",
            )
    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/logout SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/logout Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def update_info(request: Request, data: UserUpdateSchema):
    try:
        id = extentions.get_id_from_request(request)
        update_data = data.model_dump(exclude_unset=True)  # Chỉ lấy giá trị có dữ liệu
        if not update_data:
            return create_api_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="No data to update!",
            )

        user = (
            db.query(User)
            .filter_by(id=id)
            .filter(User.status == AccountStatuses.ACTIVE.value)
            .first()
        )
        if not user:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found by this token!",
            )

        # Check phone
        if "phone" in update_data:
            existing_phone = (
                db.query(User)
                .filter(User.phone == update_data["phone"], User.id != id)
                .first()
            )
            if existing_phone:
                return create_api_response(
                    status=status.HTTP_409_CONFLICT,
                    message="Phone number already registered!",
                )

        for key, value in update_data.items():
            if hasattr(user, key) and key != "id":
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return create_api_response(
            status=status.HTTP_200_OK,
            message="Update info successful!",
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/update_info SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/update_info Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def delete(request: Request, target_id: str):
    try:
        user_id = extentions.get_id_from_request(request)
        user = db.query(User).filter(User.id == user_id).first()
        user_refresh_tokens = (
            db.query(UserRefreshTokens)
            .filter(UserRefreshTokens.user_id == user_id)
            .all()
        )

        if user_id != target_id:  # If user wanna delete user having target_id
            # Check role, have permission if role admin
            if user.role == Roles.ADMIN.value:
                target_user = db.query(User).filter(User.id == target_id).first()
                if not target_user:
                    return create_api_response(
                        status=status.HTTP_404_NOT_FOUND,
                        message="User not found!",
                    )
                target_user.status = AccountStatuses.SUSPENDING.value
                db.commit()
                db.refresh(target_user)

                target_user_tokens = (
                    db.query(UserRefreshTokens)
                    .filter(UserRefreshTokens.user_id == target_id)
                    .all()
                )
                for token in target_user_tokens:
                    token.status = TokenStatuses.NON_LONGER_ACTIVE.value
                db.commit()

                return create_api_response(
                    status=status.HTTP_200_OK,
                    message="Delete account successfully!",
                )

            return create_api_response(
                status=status.HTTP_403_FORBIDDEN,
                message="You do not have permission to delete this account!",
            )
        else:  # User wanna delete him/herself
            # Check role, doesn't have permission if it is role admin
            # Because admin can not delete themselves
            if user.role == Roles.ADMIN.value:
                return create_api_response(
                    status=status.HTTP_403_FORBIDDEN,
                    message="Your account are admin account, Can not delete admin account!",
                )

            user.status = AccountStatuses.DELETED.value
            db.commit()
            db.refresh(user)

            target_user_tokens = (
                db.query(UserRefreshTokens)
                .filter(UserRefreshTokens.user_id == target_id)
                .all()
            )
            for token in target_user_tokens:
                token.status = TokenStatuses.NON_LONGER_ACTIVE.value
            db.commit()

            return create_api_response(
                status=status.HTTP_200_OK,
                message="Delete account successfully!",
            )

    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/delete SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/delete Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


async def forget_password(request: Request, email: str):
    try:
        user = (
            db.query(User)
            .filter_by(email=email)
            .filter(User.status == AccountStatuses.ACTIVE.value)
            .first()
        )
        if not user:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found",
            )

        access_token = extentions.create_access_token(
            {"id": user.id}, settings.RESET_PASS_ACCESS_TOKEN_EXPIRES_IN
        )
        email_body = templates.get_template("mail_reset_password.html").render(
            request=request,
            url=f"{settings.BASE_URL.rstrip('/')}/v1/auth/form/reset-password?name={user.name}&email={user.email}&token={access_token}",
        )
        message = MessageSchema(
            subject="[Hihand Team] - Reset password",
            recipients=[user.email],
            body=email_body,
            subtype=MessageType.html,
        )
        fm = FastMail(sendmail_config)
        await fm.send_message(message)

        return create_api_response(
            status=status.HTTP_200_OK,
            message="Email has been sent, please check your mail",
        )

    except SQLAlchemyError as e:
        logger.info(
            "SERVICE auth/send_mail_reset_password SQLAlchemyError Error: " + str(e)
        )
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        logger.info("SERVICE auth/send_mail_reset_password Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def send_form_reset_password(request: Request, name: str, email: str, token: str):
    try:

        response = templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "name": name,
                "password_regex": settings.PASSWORD_REGEX,
                "url": f"{settings.BASE_URL.rstrip('/')}/v1/auth/reset-password?email={email}&token={token}",
            },
        )

        return response

    except Exception as e:
        logger.info("SERVICE auth/send_form_reset_password Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )


def reset_password(request: Request, token: str, password: str):
    try:
        id = extentions.decode_token(token).get("id")
        if not id:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="Invalid token!",
            )
        user = (
            db.query(User)
            .filter_by(id=id)
            .filter(User.status == AccountStatuses.ACTIVE.value)
            .first()
        )
        if not user:
            return create_api_response(
                status=status.HTTP_401_UNAUTHORIZED,
                message="User not found by this token!",
            )

        user.password = extentions.hash_password(password)
        db.commit()
        db.refresh(user)

        response = templates.TemplateResponse(
            "successful_page.html",
            {
                "request": request,
                "message": "Reset password successful!",
                "url": f"{settings.BASE_URL.rstrip('/')}/docs#",
            },
        )

        return response

    except SQLAlchemyError as e:
        db.rollback()
        logger.info("SERVICE auth/reset_password SQLAlchemyError Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )

    except Exception as e:
        db.rollback()
        logger.info("SERVICE auth/reset_password Unexpected Error: " + str(e))
        return create_api_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error!",
        )
