create table if not exists role (
    "id" serial,
    name varchar(256) not null,
    "level" int not null,
    primary key("id")
);

create table if not exists file_access_lvl (
    "id" serial,
    name varchar(256) not null,
    "level" int not null,
    primary key("id")
);

create table if not exists fs_user (
    "id" serial,
    name varchar(256) not null,
    email varchar(256) not null,
    password varchar(256) not null,
    id_role int references role("id"),
    primary key("id")
);

create table if not exists file (
    "id" serial,
    name varchar(256) not null,
    id_owner int references fs_user("id"),
    primary key("id")
);

create table if not exists file_access (
    id_file int references file("id"),
    id_user int references fs_user("id"),
    id_access_lvl int references file_access_lvl("id"),
    primary key(id_file, id_user)
);