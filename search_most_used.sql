-- select *, max(cantidad_visitas)
-- from (
--   select
--     bdc.*,
--     t.idTema, t.nameTema,
--     s.idSubTemas, s.nameSubtema,
--     bd.behaviour, b.nameOfBehaviour, count(*) as cantidad_visitas
--   from behaviours_data bd
--   join behaviours b on bd.behaviour = b.idTypeBehaviour
--   join subtemas s on b.idSubTema = s.idSubTemas
--   join temas t on s.idTema = t.idTema
--   join behaviours_data_client bdc on bd.clidCod = bdc.cliCod
--   group by bd.clidCod, bd.behaviour
--   order by clidCod, count(*) desc
-- )
-- group by cliCod

-- select clidCod, behaviour, nameOfBehaviour, max(cantidad_visitas) as cantidad_visitas
-- from (
--   select bd.clidCod, bd.behaviour, b.nameOfBehaviour, count(*) as cantidad_visitas
--   from behaviours_data as bd
--   join behaviours as b on bd.behaviour = b.idTypeBehaviour
--   group by clidCod, behaviour
--   order by clidCod, count(*) desc
-- )
-- group by clidCod

-- select bd.*, count(*) as cantidad_visitas
-- from behaviours_data bd
-- join behaviours b on bd.behaviour = b.idTypeBehaviour
-- join subtemas s on b.idSubTema = s.idSubTemas
-- join temas t on s.idTema = t.idTema
-- join behaviours_data_client bdc on bd.clidCod = bdc.cliCod
-- where bd.clidCod = "{}"
-- group by bd.clidCod, bd.behaviour
-- order by cantidad_visitas desc
-- limit "{}"

select bdc.*, bd.*, count(*) as cantidad_visitas
from behaviours_data bd
join behaviours b on bd.behaviour = b.idTypeBehaviour
join subtemas s on b.idSubTema = s.idSubTemas
join temas t on s.idTema = t.idTema
join behaviours_data_client bdc on bd.clidCod = bdc.cliCod
where bd.clidCod = %s
group by bd.clidCod, bd.behaviour
order by cantidad_visitas desc
limit %s
;