import folium
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
from Application import Application

#m = folium.Map()
#r = folium.raster_layers.ImageOverlay("LC81790212015146LGN00_sr_band5.tif", bounds=[[56.963740, 34.465700], [54.815860, 38.534710]])
#r.add_to(m)
#folium.LayerControl().add_to(m)
#m.save("test.html")
app = Application()
#with open("test.html") as html:
 #   window.setHtml("\n".join(html.readlines()))
#window.show()
#!!!!!!!!!!!!! window.page().runJavaScript()
app.run()
