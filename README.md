# Projekt "Mood" Light: Lichtsteuerung per Emotion

By [Paul Theurer]

## Table of Contents

1. [Introduction](#introduction)
2. [Theorie der Emotionserkennung](#TheorieEmotion)
3. [Face & emotion recognition](#citation)
4. [Philipps HUE Ansteuerung](#lichtsteuerung)
5. [Farb-Emotionszuordnung](#models)
6. [Anleitung](#instruction)

## Introduction

Das Projetk Mood Light versucht menschliche Emotionen mithilfe neuronaler Netze zu erkennen und das Licht im Raum mithilfe vom Philipps HUE System den Emotionen anzupassen. Somit schlägt der Aufbau Brücken zwischen rationalen entscheidenden künstlichen Intelligenzen und den oft schwer zu verstehenden, irrationalen menschlichen Emotionen. Die Farbe des Lichts dient als Kommunikationsmittel zwischen dem Smart Home System und dem Menschen, wodurch in Zukunft eine Art Verstädnis simuliert werden kann. So kann das Ergebnis der Emotionserkennung im Zuhause genutzt werden, um negativen Emotionen gegenzusteuern oder einfach das Wohlfühlen zu erleichtern. Damit  dient in Zukunft das Zusammenspiel der Smarthome-Systeme dazu, "negative" Emotionen abzufangen und positive zu verstärken. Gute Laune kann zum Beispiel durch den Lieblingssong und helle angenehme Raumfarben verstärkt werden. Allerdings sieht die derzeitige Realisierung lediglich die Abbildung der Emotion auf das Licht vor und vernachlässigt außerdem die Reaktion des Menschen auf die neuen äußeren Einflüsse des "Mood" Lights. 

**Hard- & Software**
  * Raspberry Pi 4 mit 4GB Arbeitsspeicher
  * Raspberry Pi Kamera V2.1 
  * Philips HUE Bridge & 2 HUE lightbars
  * HDMI Display für den Raspberry PI 1024*600 Pixel (Für andere Auflösungen muss der Code geändert werden)
  * Versionen der verwendeten python-Bibliotheken in der Datei "ReadmyVersion.txt"
   
  * Emotionserkennung: [MicroExpNet](https://github.com/cuguilke/microexpnet): Für das Paper [hier](https://arxiv.org/pdf/1711.07011v4.pdf) klicken. \
  cugu2019microexpnet,
  Titel: MicroExpNet: An Extremely Small and Fast Model For Expression Recognition From Face Images \
  Author: Cugu, Ilke and Sener, Eren and Akbas, Emre\
  Buchtitel: 2019 Ninth International Conference on Image Processing Theory, Tools and Applications (IPTA), Seite: 1--6\
  Jahr: 2019\
  Organisation: IEEE
}
 <a name="TheorieEmotion"/a>
## Theorie der Emotionserkennung
Um das Ziel der Emotionserkennung zu erreichen, wird im folgenden Projekt der Einfachkeit halber, ausschließlich das Gesicht betrachtet. Dieses ist neben Sprache und Körpersprache eine der drei Erkennungsmerkmale für Emotionen. Obwohl Emotionen auch von Menschen häufig als subjektiv und komplex wahrgenommen werden, gibt es durchaus Gründe mithile von Maschinen eine Emotionserkennung zu realisieren. So existiert kein Konsens in der Diskussion darum, wie der Mensch selber Gefühlsausdrücke wahrnimmt. Eine Theorie geht davon aus, dass der Mensch, ähnlich wie die KI im Folgenden, auf Mustererkennung setzt. Bei dieser greift der Mensch beim Erkennen von komplexen Emotionen wie Wut oder Angst, auf die Erinnerung zurück und wendet dabei selber eine Mustererkennung auf Situationen an. Worin diese Muster bestehen ist von vielen Faktoren abhängig, und unterscheidet sich auch kulturell. Desweiteren geht die Theorie davon aus, dass wenn diese wegfallen würde, nur sogenannte Basisemotionen erkannt werden können. So konnten Probanden einer [Studie](https://www.deutschlandfunk.de/muster-theorie-der-emotionen-wie-menschen-gefuehle-erkennen.1148.de.html?dram:article_id=319223), welche nicht auf diese Mustererkennung zurückgreifen konnten auch keine komplexeren Emotionen wahrnehmen, sondern sie lediglich in die Kategorien postiv, negativ und neutral einteilen. Läge die Theorie richtig, würde die Implementierung der Mustererkennung es erlauben komplexere Emotionen zu erkennnen. Eine höhere Genauigkeit könnte durch die Betrachtung weiterer Indikatoren erzielt werden. Als Beispiel wird die Analyse der Stimme bereits in anderen Projekten umgesetzt. Dies kann sinnvoll sein, wenn die betrachtete Emotion vielleicht einfacher über Audio wahrzunehmen ist. So ist der Mensch in der Lage an der Stimme zu erkennen, ob eine Person zuvor geweint hat.

### Emotionserkennung mithilfe neuronaler Netze
Wie im vorigen Abschnitt erklärt, ist der Ansatz zur Emotionserkennug zwischen Mensch und Maschine ähnlich. Beide greifen auf ihr "Gedächtnis" zurück, um bekannte Muster auf neue Situationen anzuwenden. Ein Problem der maschinellen Emotionserkennung ist das zugrunde liegende Datenset. So wurden zur Erstellung der Datensets, also der Bilder, die das neuroanle Netz als Gedächtnis verwendet, immer Menschen aufgefordert Emotionen durch Mimik auszudrücken. Dies hat zur Folge, dass diese übertrieben dargestellt sind. Dadurch könnte ein Unterschied zu echten Emotionen bestehen, da diese vom Computer nur als Tendenz zu den künstlichen Emotionen der Datensets erkannt werden. Ein Beispiel hierfür ist das Lächeln: In den Datensets haben Menschen versucht diese Emtotion möglichst eindeutig darzustellen, wodurch oft ein breites Grinsen auf den Bildern zu sehen ist. Im Anschluss wurde diese Emotion als frölich hinterlegt. So kann ein breites Grinsen häufig als fröhlich erkannt werden. Ein leichtes Lächeln wird jetzt durch die Ähnlichkeit zum Grinsen als "happy" klassifiziert werden. Wären jetzt die Augen feucht oder gerötet, würde der Mensch dies als trauriges LächelCancel changesn erkennen, kleinen neuronalen netzen fehlt dazu die Genauigkeit. An den Kenndaten der Netze ist dies nicht zu erkennen, da ihre Genauigkeit mithilfe ebenfalls künstlicher Emotionen getestet wird. So werden im Allgemeinen reale Emotionen schlechter erkannt, als bewusst dargestellte. \
Nocheinmal zusammengefasst funktioniert die Emotionserkennung folgendermaßen: Zuerst muss ein Netz mit bestimmten Parametern erstellt werden. Zur Vereinfachung lassen wir die genaue Betrachtung dieser Parameter weg. Wichtig ist, dass die Anzahl der Pixel eines Bildes die Anzahl der Eingangsvariablen definiert. Um neuronale Netze möglichst schnell zu machen, wird die Auflösung der Bilder verringert und damit die Anzahl der Eingänge reduziert. Die Anzahl der zu erkennden Emotionen bestimmt die Anzahl der Ausgänge, welche Wahrscheinlichkeiten für die verschiedenen Zustände ausgeben und aufaddiert 100% ergeben. Zwischen Ein- und Ausgängen führt das Netz Rechenoperationen durch, bei denen unterschiedliche Regionen des Bildes unterschiedlcih gewichtet werden. Als Beispiel ist der Mund bei der Emotionserkennung ein wichtigerer Bereich als die Nase. Damit hat das Aussehen der Nase einen geringeren Einfluss auf das Ergebnis als der Mund. Nachdem das Netz erstellt wurde, beginnt das Training des Netzes. Hierbei wird ein sogenanntes Datenset zur Hand genommen. In unserem Fall handelt es sich dabei, um viele Bilder in denen unterscheidliche Emotionen dargestellt werden. Zu jedem Bild ist die passende Emotion hinterlegt. So weiß das Netz, dass das Gesicht auf dem Bild eine fröhliche Person darstellt und kann mit diesem Wissen Merkmale für fröhliche Gescihter sammeln. Nachdem das Netz fertig trainiert ist, also wenn alle Bilder durchgerechnet wurden, kann jetzt ein neues Bild in das netz gegeben werden. Hier nutzt das Netz die herausgearbeiteten Merkmale und versucht diese im neuen Bild wieder zu finden. 


### Face Detection- Gesichtserkennung
Da das neuronale Netz nur mathematische Operationen nutzt, ist es logisch, dass bei jedem Eingang auch ein Ergebnis am Ausgang vorliegt. Anders formuliert: Das Netz erkennt in einem Gegenstand (zB. einem Eimer) ebenso eine Emotion wie in einem Gesicht. Um dieses Szenario zu umgehen, und um die Genauigkeit des Netzes zu erhöhen, wird vor der Emotionserkennung, noch eine Gesichtserkennung geschaltet. So können nur Emotionen auf Gesichtern erkannt werden, und das Bild auf das Gesicht zugeschnitten werden. Durch den wahrscheinlich kleineren Bildausschnitt, steigt die Auflösung des Gesichts, wodurch das Gesicht die Emotionen besser erkennen kann.    Zur Gesichtserkennung wird die Haar Cascade von CV2, einer Python Bibliothek zur Bildverarbeitung und Computer Vision, genutzt. Hier bei handelt es sich um ein sogenanntes convolutional neural network (abk. cnn). Dabei wird immer ein kleines Fenster über das Bild geschoben und mit verschiedenen Bildbereichen mathematisch gefaltet. Dabei wird für jeden Bereich bestimmt, ob sich in diesem Bereich ein Gesicht befindet. Die Haar Cascade nutzt dabei noch bestimmte Muster, um so bestimmte Strukturen besser zu erkennen. So ähnelt die Form der Nasen einem horizontalen Balken, in dem Pixel für gewöhnlich heller sind als im Rest des Gesichts sind. Durch diesen Prozess ist es möglich eine Nase zu erkennen. Als Ausgabe gibt die Gesichtserkennung die Bildkoordinaten der Ecken des Rechtecks, dass das Gesicht enthält zurück. So kann später das Bild zugeschnitten werden.

### Emotion Recognition- Emotionserkennung
 Zur Emotionserkennung wurden zuest neuronale Netze, welche auf dem Datenset FER 2013 aufbauen genutzt. Auf dem dazugehörigen Testset wurden Genauigkeiten von ca. [70%](https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/leaderboard) erreicht. Da beim Projekt Performance ebenfalls eine Rolle spielt,  erzielten performante Netze nur um die 60%. Beim Versuch ein eigenes Netz zu trainieren wurden ca. 55% erreicht. Diese Genauigkeit wurde von Netzen, welche auf andere Datensets aufbauen übertroffen.\ Bei Recherchen wurde ich auf das Microexpnet aufmerksam, welches auffallend Ressourcensparend war und auf dem CK+ Datenset eine Genauigekeit von 84,8 % erzielte und bei dem Oulu-Casia Datenset immerhin 62,69% erzielte. Welches Datenset genutz werden soll ist dabei vor dem start des Programs im Source Code einstellbar, Die Datensets teilen sich 5 mögliche Emotionen, unterscheiden sich aber inder Anzahl der erkennbaren Emotionen, sowie in der Verteilung der Bilder pro Emotionen im Datenset.  Die Bilder pro Emotionen für die beiden Datensets sind im folgenden Bild dargestellt.
<img aling="left" src="/Bilder/Emotionen_Datenset.png" width="600"/> \
Im direkten Vergleich ist zusehen, dass CK+ zwar mehr Bilder insgesamt hat, aber diese auch auf mehr Emotionen verteilt sind. Dazu kommt, dass diese ungleich auf die Emotionen verteilt sind, was die Genauigkeit auch beeinflussen kann. Außerdem fallen bei Oulu-Casia zwei Emotionen weg. In diesem Fall "Neutral" und "Contempt" (dt. Verachtung). 

 <a name="lichtsteuerung"/a>
## Lichtsteuerung - Ansteuerung der Philipps Lampen
Die Lichtsteuerung wird zuerst getrennt von der Farbzuordnung betrachtet. Hier soll nur die Kommunikation des Raspberry Pi's mit den verwendeten HUE Lampen erklärt werden. Vor Beginn wieder die Anmerkung, dass HUE Lampen verwendet wurden, da diese im Smart Home-Bereich weit verbreitet sind. Sie liegen damit dem späteren das Raumlicht zuhause anzupassen am nächsten. Die erste Idee war die Lampen direkt über Zigbee anzusteuern. Allerdings ist diese Implementierung kompliizerter und schlechter dokumentiert. In der späteren Umsetzung verwende ich http Request über das lokale Netzwerk. Im grunde baut man dabei eine URL für alle Befehle auf. 
Als erstes ist der Befehl zum An- und Ausschalten der HUE Lampen zusehen.
```python
  def turn_on_group(where):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)
```
Bei der bridge_ip handelt es sich um die IP-Adresse der HUE Bridge. Diese kann in der Philipps HUE App gefunden werden. Der **bridge_username** muss erzeugt werden und stellt eine Art der Zugangsberechtigung dar. Ein Tutorial für die Ansteuerung der HUE Lights ist [hier](https://developers.meethue.com/develop/get-started-2/) zu finden. "pixelflux" ist dabei der Name einer angelegten HUE Gruppe. Dieser wurde in der APP bereits angelegt. Der **payload** beinhaltet die jeweiligen Befehle. "on" hat dabei die möglichen Werte "true" und "false". Ein Bespiel mit weiteren Befehlen ist bei der Einstellung der Lichtfarbe zu sehen:
```python
def switch_light_color(where,what):
    groups = { 'pixelflux': 1}
    group_id = groups[where]

    payload = {"on":True,"sat":254, "bri":254,"hue":what}
    headers = {'content-type': 'application/json'}
    r = requests.put("http://"+bridge_ip+"/api/"+bridge_username+"/groups/"+str(group_id)+"/action", data=json.dumps(payload), headers=headers)

```
 Mit den Befehlen "sat" und "bri" wird die Sättigung und die Helligkeit eingestellt. Der "what"-Parameter der Funktion ist die Farbe des Lichts. Diese ist von 1- 65.000 einstellbar. Wobei der Farbkreis auf diese Skala abgebildet wird. der Wert 0 beginnt dabei mit dunkelroten Farben und geht über orange, gelb, grün, blau wieder gegen rot. 

## Farb- zu Emotionszuordnung
Bei der Zuordnung von Emotionen zu Farbe orientiert sich die Arbeit an **"Plutchiks Wheel of Emotion"**. Dieser geht in seiner Theorie von 8 Basisemotionen aus. Diese ordnet er Farben auf dem Farbkreis zu. Diese Theorie lässt sich dreidimensional erweitern. So wird aus dem Kreis ein Kegel. Dabei setzen sich alle anderen Emotionen aus einer Mischung der Basisemotionen zusammen. Dadurch ordnet er jeder Emotion eine Farbe zu.
Zweidimensional dargestellt, ergibt sihc folgendes Muster: 

<img src="/Bilder/Farbkreis.png" width="800" /> \

### Quellen
Farbkegel: https://www.wikiwand.com/de/Robert_Plutchik
