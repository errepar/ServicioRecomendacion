select idTypeOfBehaviour
from behaviours_data
where clicod = 301180
group by idTypeOfBehaviour
order by sum(frecuBehaviour) desc