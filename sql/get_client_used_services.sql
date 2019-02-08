select idTypeOfBehaviour
from behaviours_data
where clicod = {0}
group by idTypeOfBehaviour
order by sum(frecuBehaviour) desc