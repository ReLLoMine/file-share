create table if not exists role (
    "id" serial,
    name varchar(256) not null,
    "level" int not null,
    primary key("id")
);

create table if not exists fs_user (
    "id" serial,
    name varchar(255) not null,
    email varchar(255) not null,
    password varchar(256) not null,
    id_role int references role("id"),
    primary key("id")
);

create table if not exists file (
    "id" serial,
    name varchar(255) not null,
    id_owner int references fs_user("id"),
    primary key("id")
);