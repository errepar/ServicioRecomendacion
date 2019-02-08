select bd.clicod              as CodigoCliente,
       bdc.FisJur             as TipoPersona,
       bdc.age                as Edad,
       bdc.tasaeol            as TasaEOL,
       bdc.tasaius            as TasaIUS,
       bdc.debaut             as DebitoAutomatico,
       bdc.score              as Score,
       t.nameTema             as NameTema,
       t.idTema               as IdTema,
       s.idSubTemas           as IdSubtema,
       b.nameOfBehaviour      as NameBehaviour,
       bd.idTypeOfBehaviour      as IdBehaviour,
       sum(bd.frecuBehaviour) as CantidadVisitas
from behaviours_data as bd
       join behaviours_data_client as bdc on bd.clicod = bdc.cliCod
       join behaviours b on bd.idTypeOfBehaviour = b.idTypeBehaviour
       join subtemas s on b.idSubTema = s.idSubTemas
       join temas t on s.idTema = t.idTema
where bd.clicod = {0}
-- where bd.clicod = 301180
group by bd.NameOfBehaviour
order by cantidadVisitas desc
-- limit 5
limit {1}
