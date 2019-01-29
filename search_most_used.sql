select bd.clicod as CodigoCliente, bdc.FisJur as TipoPersona, bdc.age as Edad, bdc.tasaeol as TasaEOL, bdc.tasaius as TasaIUS, bdc.debaut as DebitoAutomatico, bdc.score as Score,
       t.idTema as IdTema, s.idSubTemas as IdSubtema, b.idTypeBehaviour as IdBehaviour, sum(bd.frecuBehaviour) as CantidadVisitas
from behaviours_data as bd
join behaviours_data_client as bdc on bd.clicod = bdc.cliCod
join behaviours b on bd.NameOfBehaviour = b.nameOfBehaviour
join subtemas s on bd.NameSubTema = s.nameSubtema
join temas t on bd.NameTema = t.nameTema
where bd.clicod = %s
group by bd.NameOfBehaviour
order by cantidadVisitas desc
limit %s