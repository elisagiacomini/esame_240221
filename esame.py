# Creo la classe ExamException
class ExamException(Exception):
    pass

# Creo la classe CSVFile
class CSVTimeSeriesFile:

    # La classe creata deve essere istanziata sul nome del file tramite la variabile name
    def __init__(self, name):
        self.name = name
    
    def get_data(self):
        # La classe deve avere un metodo che mi ritorni una lista di liste, dove il primo elemento delle liste annidate è l’epoch ed il secondo la temperatura.
        listafinale = []

        # Apro il file
        try:
            file = open(self.name,'r')
        except Exception as e:
            # se non riesco ad aprire il file alzo un'eccezione
            raise ExamException('Problema nella lettura del file: "{}"'.format(e))

        # Lettura del file riga per riga
        for riga in file:
            # Faccio lo split di ogni riga sulla virgola
            dati = riga.split(',')

            # Se non sono sulla prima riga...
            if dati[0] != 'epoch':
                # ...setto epoch e temperature
                epoch = dati[0]
                temperature = dati[1]

                # Converto epoch in int tramite arrotondamento con round()
                try:
                    epoch = round(float(epoch))
                except Exception as e:
                    # Tutto deve procedere comunque, quindi non alzo nessuna eccezione
                    continue

                # Converto le temperature in float e non alzo eccezioni
                try:
                    temperature = float(temperature)
                except Exception as e:
                    continue

                # Controllo l'ordine dei timestamp
                timestamp_pre = -1 # Qualsiasi numero inserito sarà maggiore di -1
                for listasingola in listafinale:
                    if listasingola[0] <= timestamp_pre:
                        raise ExamException('Timestamp fuori ordine o timestamp duplicati.')
                    timestamp_pre = listasingola[0]
                
                # Creo una lista (listasingola)
                listasingola = [epoch, temperature]
                # e aggiungo la listasingola alla listafinale
                listafinale.append(listasingola)

        # Chiudo ilfile
        file.close()

        return listafinale


# Creo la funzione principale per calcolare i trend di temperatura 
def hourly_trend_changes(time_series):

    # L'output sarà
    lista_variazioni_totale=[]

    # Creo una lista in cui metterò l'inizio dell'ora per ogni epoch
    # Creo una lista che contiene gli epoch della stessa ora
    ora_epoch=[]
    for item in time_series:
        ora_epoch.append(int(item[0]/3600))

    # Pongo i=0 l'indice che utilizzerò per muovermi nella lista ora_epoch
    i = 0

    # Dato che i valori inizali delle ore cambiano a seconda dell'ora precedente, creo due liste

    # ultimo_cresce è la lista in cui metto dentro il valore de trend, cioè se il trend cresce o decresce
    # Questa lista contiene valori True/False
    # Quando entro in una nuova ora, accedendo a ultimo_cresce riesco a capire se prima il trend era in positivo o in negativo
    ultimo_cresce = []

    # ultimo_valore tiene a mente l'ultimo valore di un'ora
    # Mi serve perchè quando entro in una nuova ora devo sapere quale era l'ultimo valore dell'ora precedente per capire se c'è già un trend di temperatura o no
    ultimo_valore = []

        
    while i<len(ora_epoch):
        # Creo una lista in cui vengono inserite le temperature della stessa ora
        # In questa lista metto già dentro il primo valore dell'ora corrente
        # Per creare questa lista sfrutto il fatto che, passando gli elementi del vettore, non appena si trova un elemento appartenente all'ora successiva, la lista non viene più riempita, e vengono svolte le operazioni successive
        lista_temperature_ora = [time_series[i][1]]

        variazioni_trend = 0 # variabile per contare le variazioni di trend

        j = i + 1 # fissata l'ora i-esima,parto dall'elemento successivo

        #confronto per vedere se i due elementi sono nella stessa ora
        ora_successiva = False # Questa variabile diventa vera appena cambio ora
        

        while j<len(ora_epoch) and ora_successiva is False:
            # Se due epoch appartengono alla stessa ora
            if ora_epoch[j]==ora_epoch[i]:
                lista_temperature_ora.append(time_series[j][1])
                j+=1

            else:
                # ora_epoch[j] appartiene all'ora successiva
                ora_successiva=True

                # Calcolo le variazioni di trend dell'ora
                if i==0:#se primo giro
                    variazioni_trend = variazione_trend_prima_ora(lista_temperature_ora,ultimo_valore,ultimo_cresce)

                if i>0:
                    variazioni_trend = variazione_trend(lista_temperature_ora,ultimo_valore,ultimo_cresce)    

                
                i=j#cosi' ora_epoch[i] sara' la nuova ora

                #aggiungo il risultato alla lista_variazioni_totale
                lista_variazioni_totale.append(variazioni_trend)

        #Caso in cui sono arrivato all'ultimo elemento di ora_epoch
        #non potevo usare il while sopra:l'ultimo elemento non ha un successivo!

        if j==len(ora_epoch):
            #CALCOLO VARIAZIONI DI TREND DELL'ORA
            variazioni_trend= variazione_trend(lista_temperature_ora,ultimo_valore,ultimo_cresce)    

            #aggiungo il risultato alla lista_variazioni_totale
            lista_variazioni_totale.append(variazioni_trend)

            i=j


    return lista_variazioni_totale



# Per il primo giro uso un'altra funzione perchè all'inizio della lista devo capire se il trend sta crescendo o decrescendo
# Se sono nella prima ora posso capirlo guardando la variazione che c'è tra il primo e secondo elemento
def variazione_trend_prima_ora(lista,ultimo_valore,ultimo_cresce):

    conta_variazioni = 0

    # Caso specifico in cui la lista ha solo un elemento (quindi avrò 0 variazioni)
    if len(lista)==1:

        # In questo caso basta che io aggiorni la lista ultimo_valore
        ultimo_valore.append(lista[-1])

        #nb non aggiungo nulla a ultimo valore perchè non posso dire nulla sul trend

        return conta_variazioni

    else:

        if lista[0]<lista[1]:
            # Creo una variabile vero/falso che mi dice se il trend cresce o no
            # In questo caso il trend cresce
            cresce=True

        else:
            # Qui il trend non cresce
            cresce=False

        for i in range(1,len(lista)-1):

            if cresce is True and lista[i]>lista[i+1]:
                cresce=False

                conta_variazioni+=1

            if cresce is False and lista[i]<lista[i+1]:
                cresce=True

                conta_variazioni+=1

        #considero l'ultimo valore e il trend attuale
        #mi servirà per l'altra funzione

        ultimo_valore.append(lista[-1])
        ultimo_cresce.append(cresce)

    
    return conta_variazioni


#funzione per i casi successivi
def variazione_trend(lista,ultimo_valore,ultimo_cresce):

    conta_variazioni=0
    #caso particolare in cui nella prima ora ha solo una temperatura

    if  len(ultimo_cresce)==0:
        if (lista[0]-ultimo_valore[-1])>=0:
            cresce=True
        else:
            cresce=False
    else:#se avevo già il trend precedente no problem
        cresce=ultimo_cresce[-1]

    #valuto il primo elemento in base al trend precedente

    if cresce is True and (lista[0]-ultimo_valore[-1])<0:
        conta_variazioni+=1
        cresce= False#cambio il trend  

    if cresce is False and (lista[0]-ultimo_valore[-1])>0:
        conta_variazioni+=1
        cresce= True#cambio il trend


    if len(lista)==1:#se la lista ha un elemento solo 
        #aggiorno ultimo_valore e ultimo_cresce
        ultimo_valore.append(lista[-1])
        ultimo_cresce.append(cresce)

        return conta_variazioni

    else:#se la lista ha più elementi

        for i in range(0,len(lista)-1):

            if cresce is True and lista[i]>lista[i+1]:
                cresce=False
                conta_variazioni+=1

            if cresce is False and lista[i]<lista[i+1]:
                cresce=True
                conta_variazioni+=1

        #aggiorno ultimo valore e ultimo cresce

        ultimo_valore.append(lista[-1])

        ultimo_cresce.append(cresce)


    return conta_variazioni



time_series_file = CSVTimeSeriesFile(name = 'data.csv')
time_series = time_series_file.get_data()


# Printo il nome dei file e i dati contenuti nel file
print('Nome del file: "{}"'.format(time_series_file.name))

print('Dati contenuti nel file:')
print('[')
for elementi in time_series_file.get_data():
    print(" {},".format(elementi))
print(']')

# Stampo lista che contiene i trend di temperatura per ogni ora
lista_risultato= hourly_trend_changes(time_series)
print(lista_risultato)