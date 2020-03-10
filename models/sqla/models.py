# coding: utf-8
#sqlacodegen mysql+pymysql://root:root@mysql/dispensary --outfile models/sqla/models.py

from sqlalchemy import CHAR, Column, DateTime, Float, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.orm import relationship
from .database import Base

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    name = Column(CHAR(255))


class Module(Base):
    __tablename__ = 'modules'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    name = Column(CHAR(255))


class Role(Base):
    __tablename__ = 'roles'

    id = Column(BIGINT(20), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)


class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT(20), primary_key=True)
    email = Column(CHAR(255), nullable=False, unique=True, server_default=text("''"))
    password = Column(CHAR(255), nullable=False)
    active = Column(TINYINT(1), nullable=False)


class AgentsModule(Base):
    __tablename__ = 'agents_modules'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    agent_id = Column(ForeignKey('agents.id'), index=True)
    module_id = Column(ForeignKey('modules.id'), index=True)

    agent = relationship('Agent')
    module = relationship('Module')


class Device(Base):
    __tablename__ = 'devices'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    device_account_id = Column(ForeignKey('device_accounts.id'), nullable=False, index=True)
    device_id = Column(String(255), nullable=False)

    device_account = relationship('DeviceAccount')


class Intent(Base):
    __tablename__ = 'intents'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    name = Column(CHAR(255), nullable=False)
    module_id = Column(ForeignKey('modules.id'), index=True)

    module = relationship('Module')


class UsersRole(Base):
    __tablename__ = 'users_roles'

    id = Column(BIGINT(20), primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    role_id = Column(ForeignKey('roles.id'), nullable=False, index=True)

    role = relationship('Role')
    user = relationship('User')


class IntentContext(Base):
    __tablename__ = 'intent_contexts'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    intent_id = Column(ForeignKey('intents.id'), index=True)
    text = Column(Text)

    intent = relationship('Intent')


class IntentDialog(Base):
    __tablename__ = 'intent_dialogs'

    id = Column(BIGINT(20), primary_key=True)
    intent_id = Column(ForeignKey('intents.id'), nullable=False, index=True)
    name = Column(CHAR(255), nullable=False)
    slot = Column(CHAR(255))
    input_type = Column(CHAR(255))

    intent = relationship('Intent')


class IntentPattern(Base):
    __tablename__ = 'intent_patterns'

    id = Column(BIGINT(20), primary_key=True, unique=True)
    intent_id = Column(ForeignKey('intents.id'), nullable=False, index=True)
    text = Column(Text, nullable=False)

    intent = relationship('Intent')


class IntentResponse(Base):
    __tablename__ = 'intent_responses'

    id = Column(BIGINT(20), primary_key=True)
    intent_id = Column(ForeignKey('intents.id'), nullable=False, index=True)
    text = Column(Text, nullable=False)

    intent = relationship('Intent')

