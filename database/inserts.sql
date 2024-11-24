insert into role (name, "level")
    select * from (select 'admin', 1) as tmp
    where not exists (
        select * from role where name = 'admin' and "level" = 1
    ) limit 1;

insert into role (name, "level")
    select * from (select 'user', 2) as tmp
    where not exists (
        select * from role where name = 'user' and "level" = 2
    ) limit 1;

insert into role (name, "level")
    select * from (select 'guest', 3) as tmp
    where not exists (
        select * from role where name = 'guest' and "level" = 3
    ) limit 1;

insert into file_access_lvl (name, "level")
    select * from (select 'read', 1) as tmp
    where not exists (
        select * from file_access_lvl where name = 'read' and "level" = 1
    ) limit 1;

insert into file_access_lvl (name, "level")
    select * from (select 'write', 2) as tmp
    where not exists (
        select * from file_access_lvl where name = 'write' and "level" = 2
    ) limit 1;

insert into file_access_lvl (name, "level")
    select * from (select 'delete', 3) as tmp
    where not exists (
        select * from file_access_lvl where name = 'delete' and "level" = 3
    ) limit 1;

insert into file_access_lvl (name, "level")
    select * from (select 'owner', 4) as tmp
    where not exists (
        select * from file_access_lvl where name = 'owner' and "level" = 4
    ) limit 1;

-- add guest user
insert into fs_user (id, email, name, password, id_role)
    select * from (select 1, 'guest@mail.com', 'guest', 'password', (select id from role where name = 'guest')) as tmp
    where not exists (
        select * from fs_user where id = 1 and email = 'guest@mail.com' and name = 'guest' and password = 'password' and id_role = (select id from role where name = 'guest')
    ) limit 1;

-- add file_access to owners
insert into file_access (id_file, id_user, id_access_lvl)
    select f.id, u.id, fal.id
    from file as f, fs_user as u, file_access_lvl as fal
    where f.id_owner = u.id and fal.name = 'owner' and not exists (
        select * from file_access where id_file = f.id and id_user = u.id and id_access_lvl = fal.id
    );