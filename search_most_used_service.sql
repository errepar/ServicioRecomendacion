select bdc.*, bd.clidCod, t.idTema, t.nameTema, s.idSubTemas, s.nameSubtema, bd.behaviour, b.nameOfBehaviour, count(*) as cantidad_visitas
from behaviours_data bd
join behaviours b on bd.behaviour = b.idTypeBehaviour
join subtemas s on b.idSubTema = s.idSubTemas
join temas t on s.idTema = t.idTema
join behaviours_data_client bdc on bd.clidCod = bdc.cliCod
group by bd.clidCod, bd.behaviour
order by clidCod, count(*) desc
