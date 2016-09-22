# QGIS Logistics #

Wtyczka do QGIS-a, która na podstawie podanych kodów pocztowych zwraca trasę pomiędzy centroidami tych kodów, a także poligon obszaru w odległości X metrów od tej trasy.

Przy routingu użyto API projektu Skobbler. Skobbler API key można podmienić w `config.py`
Więcej o Skobbler - [developer.skobbler.com](http://developer.skobbler.com/)

Poligon jest buforem o wielkości X metrów wdłuż wyznaczonej trasy.

