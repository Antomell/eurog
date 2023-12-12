#Settare La Versione
#Settare gli url(accesso,logo,aggiornamenti)

import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from tkcalendar import DateEntry
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import date, datetime
from tkinter import PhotoImage
import subprocess
import requests
import sys

# Inizializzazione dell'app Firebase
cred = credentials.Certificate("/Users/antonio/Desktop/EuroGames/apptest2-b0057-firebase-adminsdk-t50ig-07570d3c6c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Variabile globale per l'elenco delle slot
slots = []

# Dizionario per memorizzare lo stato dei colori dei label
label_colors = {}

# Configurazioni per la visualizzazione scorrevole
scroll_height = 19  # Altezza massima della visualizzazione scorrevole
scroll_start_index = 0  # Indice di inizio della visualizzazione scorrevole

#Versione Corrente da modificare agli aggiornamenti
versione_corrente = "1.0.0"

#Variabile Data Selezionata default
data_inizio = None
data_inizio_formattata = None
data_fine = None
data_fine_formattata = None

# Funzione per l'aggiunta di una nuova slot
def aggiungi_slot():
    giri_effettuati = None  # Dichiarazione della variabile globale

    def campi_compilati():
        if (
            nome_entry.get() == ''
            or ubicazione_entry.get() == ''
            or saldo_entry.get() == ''
            or numero_scheda_entry.get() == ''
            or id_macchina_entry.get() == ''
            or giri_effettuati_entry.get() == '' 
        ):
            return False
        return True

    def saldo_format_corretto(saldo):
        try:
            float(saldo)
            return True
        except ValueError:
            return False

    def salva_slot():
        nonlocal giri_effettuati  # Usa la variabile esterna

        if not campi_compilati():
            messagebox.showerror("Errore", "Compila tutti i campi.")
            return

        saldo_iniziale = saldo_entry.get()

        if not saldo_format_corretto(saldo_iniziale):
            messagebox.showerror("Errore", "Il formato del saldo iniziale non è corretto. Inserire un valore numerico nel formato x.xx.")
            return

        nome = nome_entry.get()
        ubicazione = ubicazione_entry.get()
        saldo = saldo_entry.get()
        numero_scheda = numero_scheda_entry.get()
        id_macchina = id_macchina_entry.get()
        giri_effettuati = giri_effettuati_entry.get()

        # Data di creazione della slot
        data_creazione = datetime.now()

        # Salvataggio dei dati nel database Firestore
        doc_ref = db.collection(u'slots').document()
        doc_ref.set({
            u'nome': nome,
            u'nome_lowercase': nome.lower(),
            u'ubicazione': ubicazione,
            u'saldo_iniziale': saldo,
            u'saldo': saldo,
            u'numero_scheda': numero_scheda,
            u'id_macchina': id_macchina,
            u'giri_effettuati': giri_effettuati,
            u'data_selezionata': cal.get_date(),
            u'data_e_ora_creazione': data_creazione.strftime("%d/%m/%Y %H:%M:%S")
        })
        messagebox.showinfo("Successo", "Slot aggiunta con successo")
        finestra_aggiungi_slot.destroy()

        aggiorna_lista_slot()
        aggiorna_numero_slot()

    def esc_aggiungi_slot():
        finestra_aggiungi_slot.destroy()

    finestra_aggiungi_slot = tk.Toplevel()
    finestra_aggiungi_slot.title("Aggiungi Slot")

    finestra_aggiungi_slot.update_idletasks()
    finestra_width = 300  # Imposta la larghezza desiderata della finestra
    finestra_height = 550  # Imposta l'altezza desiderata della finestra
    screen_width = finestra_aggiungi_slot.winfo_screenwidth()
    screen_height = finestra_aggiungi_slot.winfo_screenheight()
    x = (screen_width // 2) - (finestra_width // 2)
    y = (screen_height // 2) - (finestra_height // 2)
    finestra_aggiungi_slot.geometry(f"{finestra_width}x{finestra_height}+{x}+{y}")

    finestra_aggiungi_slot.resizable(False, False)  # Imposta la finestra come non ridimensionabile

    nome_label = tk.Label(finestra_aggiungi_slot, text="Nome: ")
    nome_label.pack()
    nome_entry = tk.Entry(finestra_aggiungi_slot)
    nome_entry.pack()

    ubicazione_label = tk.Label(finestra_aggiungi_slot, text="Ubicazione: ")
    ubicazione_label.pack()
    ubicazione_entry = tk.Entry(finestra_aggiungi_slot)
    ubicazione_entry.pack()

    saldo_label = tk.Label(finestra_aggiungi_slot, text="Saldo Iniziale: ")
    saldo_label.pack()
    saldo_entry = tk.Entry(finestra_aggiungi_slot)
    saldo_entry.pack()

    numero_scheda_label = tk.Label(finestra_aggiungi_slot, text="Numero Scheda: ")
    numero_scheda_label.pack()
    numero_scheda_entry = tk.Entry(finestra_aggiungi_slot)
    numero_scheda_entry.pack()

    id_macchina_label = tk.Label(finestra_aggiungi_slot, text="ID Macchina: ")
    id_macchina_label.pack()
    id_macchina_entry = tk.Entry(finestra_aggiungi_slot)
    id_macchina_entry.pack()


    giri_effettuati_label = tk.Label(finestra_aggiungi_slot, text="Giri Effettuati: ")
    giri_effettuati_label.pack()
    giri_effettuati_entry = tk.Entry(finestra_aggiungi_slot)
    giri_effettuati_entry.pack()

    cal_label = tk.Label(finestra_aggiungi_slot, text="Seleziona Data Di Inserimento Slot:")
    cal_label.pack()

    today = date.today()
    cal = Calendar(finestra_aggiungi_slot, selectmode='day', year=today.year, month=today.month, day=today.day, maxdate=today)
    cal.pack()

    salva_button = tk.Button(finestra_aggiungi_slot, text="Salva", command=salva_slot)
    salva_button.pack()
    finestra_aggiungi_slot.bind("<Return>", lambda event: salva_slot())  # Aggiungi il binding del tasto Invio
    finestra_aggiungi_slot.bind("<Escape>", lambda event: esc_aggiungi_slot())

# Funzione per la modifica di una slot
def modifica_slot(slot_id):
    saldo_prima_modifica = None
    giri_prima_modifica = None

    def salva_modifiche():
        nonlocal saldo_prima_modifica, giri_prima_modifica

        nome = nome_entry.get()
        ubicazione = ubicazione_entry.get()
        saldo = saldo_entry.get()
        numero_scheda = numero_scheda_entry.get()
        id_macchina = id_macchina_entry.get()
        giri_effettuati = giri_effettuati_entry.get()

        # Controllo sui campi vuoti
        if not nome or not ubicazione or not saldo or not numero_scheda or not id_macchina or not giri_effettuati:
            messagebox.showerror("Errore", "Compila tutti i campi.")
            return

        # Controllo sul formato del saldo
        if not saldo_format_corretto(saldo):
            messagebox.showerror("Errore", "Il formato del saldo non è corretto. Inserire un valore numerico nel formato X.XX")
            return

        # Recupero il valore attuale del saldo e giri effettuati dal database Firestore prima dell'aggiornamento
        doc_ref = db.collection(u'slots').document(slot_id)
        slot_prima_modifica = doc_ref.get().to_dict()
        saldo_prima_modifica = float(slot_prima_modifica["saldo"])
        giri_prima_modifica = int(slot_prima_modifica["giri_effettuati"])

        # Aggiornamento dei dati nel database Firestore
        doc_ref.update({
            u'nome': nome,
            u'nome_lowercase': nome.lower(),
            u'ubicazione': ubicazione,
            u'saldo': saldo,  # Converti il saldo in stringa
            u'numero_scheda': numero_scheda,
            u'id_macchina': id_macchina,
            u'giri_effettuati': giri_effettuati
        })

        # Calcola la differenza tra il saldo e i giri dopo e prima della modifica
        saldo_dopo_modifica = float(saldo)
        saldo_modificato = saldo_dopo_modifica - saldo_prima_modifica
        giri_dopo_modifica = int(giri_effettuati)
        giri_modificati = giri_dopo_modifica - giri_prima_modifica

        # Converti i saldi in stringhe prima di inserirli nel documento storico_saldi
        saldo_str = str(saldo)
        saldo_prima_modifica_str = str(saldo_prima_modifica)
        saldo_modificato_str = str(saldo_modificato)

        # Aggiungi una voce nel documento "storico_saldi" con il saldo e i giri prima della modifica e le differenze
        storico_ref = doc_ref.collection(u'storico_saldi').document()
        storico_ref.set({
            u'data_ora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            u'data_aggiunta': datetime.now().strftime("%Y-%m-%d"),
            u'saldo_aggiunto': saldo_str,
            u'giri_aggiunti': giri_effettuati,  # Aggiungi il numero di giri effettuati
            u'tipo_modifica': "Slot Modificata",
            u'saldo_prima_modifica': saldo_prima_modifica_str,
            u'differenza_saldo': saldo_modificato_str,
            u'giri_prima_modifica': str(giri_prima_modifica),
            u'differenza_giri': str(giri_modificati)
        })

        messagebox.showinfo("Successo", "Modifiche salvate con successo")
        finestra_modifica_slot.destroy()

        aggiorna_lista_slot()
        aggiorna_numero_slot()  # Aggiorna la lista delle slot dopo aver salvato le modifiche

    def saldo_format_corretto(saldo):
        try:
            float(saldo)
            return True
        except ValueError:
            return False

    def esc_modifica_slot():
        finestra_modifica_slot.destroy()

    finestra_modifica_slot = tk.Toplevel()
    finestra_modifica_slot.title("Modifica Slot")

    finestra_modifica_slot.update_idletasks()
    finestra_width = 300  # Larghezza desiderata della finestra
    finestra_height = 350  # Altezza desiderata della finestra
    screen_width = finestra_modifica_slot.winfo_screenwidth()
    screen_height = finestra_modifica_slot.winfo_screenheight()
    x = (screen_width // 2) - (finestra_width // 2)
    y = (screen_height // 2) - (finestra_height // 2)
    finestra_modifica_slot.geometry(f"{finestra_width}x{finestra_height}+{x}+{y}")

    finestra_modifica_slot.resizable(False, False)  # Imposta la finestra come non ridimensionabile

    # Recupero dei dati della slot dal database Firestore
    doc_ref = db.collection(u'slots').document(slot_id)
    slot = doc_ref.get().to_dict()

    nome_label = tk.Label(finestra_modifica_slot, text="Nome:")
    nome_label.pack()
    nome_entry = tk.Entry(finestra_modifica_slot)
    nome_entry.insert(tk.END, slot["nome"])
    nome_entry.pack()

    ubicazione_label = tk.Label(finestra_modifica_slot, text="Ubicazione:")
    ubicazione_label.pack()
    ubicazione_entry = tk.Entry(finestra_modifica_slot)
    ubicazione_entry.insert(tk.END, slot["ubicazione"])
    ubicazione_entry.pack()

    saldo_label = tk.Label(finestra_modifica_slot, text="Saldo Attuale:")
    saldo_label.pack()
    saldo_entry = tk.Entry(finestra_modifica_slot)
    saldo_entry.insert(tk.END, slot["saldo"])
    saldo_entry.pack()

    numero_scheda_label = tk.Label(finestra_modifica_slot, text="Numero Scheda:")
    numero_scheda_label.pack()
    numero_scheda_entry = tk.Entry(finestra_modifica_slot)
    numero_scheda_entry.insert(tk.END, slot["numero_scheda"])
    numero_scheda_entry.pack()

    id_macchina_label = tk.Label(finestra_modifica_slot, text="ID Macchina:")
    id_macchina_label.pack()
    id_macchina_entry = tk.Entry(finestra_modifica_slot)
    id_macchina_entry.insert(tk.END, slot["id_macchina"])
    id_macchina_entry.pack()

    giri_effettuati_label = tk.Label(finestra_modifica_slot, text="Giri Effettuati:")
    giri_effettuati_label.pack()
    giri_effettuati_entry = tk.Entry(finestra_modifica_slot)
    giri_effettuati_entry.insert(tk.END, slot["giri_effettuati"])  # Inserisci il valore attuale
    giri_effettuati_entry.pack()

    salva_button = tk.Button(finestra_modifica_slot, text="Salva", command=salva_modifiche)
    salva_button.pack()
    finestra_modifica_slot.bind("<Return>", lambda event: salva_modifiche())  # Aggiungi il binding del tasto Invio
    finestra_modifica_slot.bind("<Escape>", lambda event: esc_modifica_slot())

# Funzione per l'eliminazione di una slot
def elimina_slot(slot_id):
    conferma = messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare questa slot?")
    if conferma:
        # Eliminazione della slot dal database Firestore
        doc_ref = db.collection(u'slots').document(slot_id)
        doc_ref.delete()
        messagebox.showinfo("Successo", "Slot eliminata con successo")

        aggiorna_lista_slot()  # Aggiorna la lista delle slot dopo aver eliminato una slot
        aggiorna_numero_slot()



def aggiungi_saldo(slot_id):
    def salva_saldo():
        saldo_da_aggiungere = saldo_entry.get()  # Saldo da aggiungere viene trattato come stringa
        giri_da_aggiungere = giri_entry.get()  # Numero di giri da aggiungere

        # Controllo sul formato del saldo
        if not saldo_format_corretto(saldo_da_aggiungere):
            messagebox.showerror("Errore", "Il formato del saldo non è corretto. Inserire un valore numerico nel formato x.xx.")
            return

        # Controllo sul formato del numero di giri
        if not giri_format_corretto(giri_da_aggiungere):
            messagebox.showerror("Errore", "Il formato del numero di giri non è corretto. Inserire un valore numerico intero.")
            return

        # Recupera il valore attuale del saldo e giri effettuati dal database Firestore
        doc_ref = db.collection(u'slots').document(slot_id)
        slot = doc_ref.get().to_dict()
        saldo_attuale = float(slot["saldo"])
        giri_attuali = int(slot["giri_effettuati"])

        # Calcola il nuovo saldo e giri come stringa
        nuovo_saldo = str(saldo_attuale + float(saldo_da_aggiungere))
        nuovi_giri = str(giri_attuali + int(giri_da_aggiungere))

        # Calcola la differenza tra il nuovo saldo e il saldo attuale
        differenza_saldo = float(nuovo_saldo) - saldo_attuale

        # Calcola la differenza tra i nuovi giri e i giri attuali
        differenza_giri = int(nuovi_giri) - giri_attuali

        # Calcola la percentuale di guadagno
        guadagno = (float(nuovo_saldo) / 30000) * 100

        # Aggiorna il campo 'saldo' e 'giri_effettuati' nel database Firestore
        doc_ref.update({
            u'saldo': str(nuovo_saldo),  # Converti il saldo in stringa
            u'giri_effettuati': nuovi_giri  # Numero di giri è già una stringa
        })

        # Converti il saldo attuale in stringa prima di inserirlo nel documento storico_saldi
        saldo_attuale_str = str(saldo_attuale)

        # Salva la data e l'ora dell'operazione nel documento "storico_saldi"
        storico_ref = doc_ref.collection(u'storico_saldi').document()
        storico_ref.set({
            u'data_ora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            u'data': datetime.now().strftime("%Y-%m-%d"),
            u'saldo_aggiunto': str(saldo_da_aggiungere),
            u'giri_aggiunti': str(giri_da_aggiungere),
            u'tipo_modifica': "Saldo e Giri Aggiunti",
            u'saldo_prima_modifica': saldo_attuale_str,  # Converti il saldo attuale in stringa
            u'differenza_saldo': str(differenza_saldo),  # Converti la differenza in stringa
            u'giri_prima_modifica': str(giri_attuali),  # Converti i giri attuali in stringa
            u'differenza_giri': str(differenza_giri)  # Converti la differenza giri in stringa
        })

        # Aggiorna il colore del testo del saldo in base alla percentuale di guadagno
        if guadagno > 15:
            label_colors[slot_id] = {
                "percentuale": "black"
            }
        else:
            label_colors[slot_id] = {
                "percentuale": "red"
            }

        messagebox.showinfo("Successo", "Saldo e Giri aggiunti con successo")
        finestra_aggiungi_saldo.destroy()

        aggiorna_lista_slot()  # Aggiorna la lista delle slot dopo aver aggiunto il saldo
        aggiorna_numero_slot()

    def saldo_format_corretto(saldo):
        try:
            float(saldo)
            return True
        except ValueError:
            return False

    def giri_format_corretto(giri):
        try:
            int(giri)
            return True
        except ValueError:
            return False

    def esc_aggiungi_saldo():
        finestra_aggiungi_saldo.destroy()

    finestra_aggiungi_saldo = tk.Toplevel()
    finestra_aggiungi_saldo.title("Aggiungi Saldo")

    finestra_aggiungi_saldo.update_idletasks()
    finestra_width = 300  # Imposta la larghezza desiderata della finestra
    finestra_height = 150  # Imposta l'altezza desiderata della finestra
    screen_width = finestra_aggiungi_saldo.winfo_screenwidth()
    screen_height = finestra_aggiungi_saldo.winfo_screenheight()
    x = (screen_width // 2) - (finestra_width // 2)
    y = (screen_height // 2) - (finestra_height // 2)
    finestra_aggiungi_saldo.geometry(f"{finestra_width}x{finestra_height}+{x}+{y}")

    finestra_aggiungi_saldo.resizable(False, False)  # Imposta la finestra come non ridimensionabile

    saldo_label = tk.Label(finestra_aggiungi_saldo, text="Saldo da Aggiungere:")
    saldo_label.pack()
    saldo_entry = tk.Entry(finestra_aggiungi_saldo)
    saldo_entry.pack()

    giri_label = tk.Label(finestra_aggiungi_saldo, text="Giri da Aggiungere:")
    giri_label.pack()
    giri_entry = tk.Entry(finestra_aggiungi_saldo)
    giri_entry.pack()

    salva_button = tk.Button(finestra_aggiungi_saldo, text="Salva", command=salva_saldo)
    salva_button.pack()
    finestra_aggiungi_saldo.bind("<Return>", lambda event: salva_saldo())  # Aggiungi il binding del tasto Invio
    finestra_aggiungi_saldo.bind("<Escape>", lambda event: esc_aggiungi_saldo())


# Funzione per la ricerca di una slot
def cerca_slot(event=None):
    keyword = ricerca_entry.get().lower()

    if keyword:
        # Recupero delle slot dal database Firestore che contengono la parola chiave nella loro denominazione (case-insensitive)
        global slots
        slots = list(db.collection(u'slots').where(u'nome_lowercase', '>=', keyword).where(u'nome_lowercase', '<=', keyword + u'\uf8ff').stream())
    else:
        # Utilizza l'elenco completo delle slot
        slots = list(db.collection(u'slots').stream())

    aggiorna_visualizzazione_slot()
    aggiorna_numero_slot()

def aggiorna_lista_slot():
    # Recupero delle slot dal database Firestore
    global slots  # Utilizza la variabile globale
    slots = db.collection(u'slots').get()

    aggiorna_visualizzazione_slot()  # Aggiorna la visualizzazione delle slot
    aggiorna_numero_slot()

# Funzione per l'aggiornamento della visualizzazione delle slot
# Aggiorna la visualizzazione delle slot

def aggiorna_visualizzazione_slot():
    # Pulizia della visualizzazione
    for widget in lista_slot_frame.winfo_children():
        widget.destroy()

    # Creazione degli elementi nella visualizzazione
    index = scroll_start_index
    while index < len(slots) and index < scroll_start_index + scroll_height:
        slot = slots[index]
        slot_data = slot.to_dict()
        slot_frame = tk.Frame(lista_slot_frame, pady=5)
        slot_frame.pack(fill="x", padx=10)

        nome_label = tk.Label(slot_frame, text="Nome: " + slot_data["nome"], width=15, anchor="w")
        nome_label.pack(side=tk.LEFT)

        ubicazione_label = tk.Label(slot_frame, text="Ubicazione: " + slot_data["ubicazione"], width=20, anchor="w")
        ubicazione_label.pack(side=tk.LEFT)

        if data_inizio is None and data_fine is None:
            saldo_label = tk.Label(slot_frame, text=f"Saldo: {slot_data['saldo']}", width=15, anchor="w")
            saldo_label.pack(side=tk.LEFT)

            percentuale_label = tk.Label(slot_frame, text="Percentuale: {:.2f}%".format((float(slot_data["saldo"]) / 30000) * 100), width=15, anchor="w")
            percentuale_label.pack(side=tk.LEFT)
            
        else:
            if "storico_saldi" in slot_data and isinstance(slot_data["storico_saldi"], list):
                saldo_totale = 0
                for modifica in slot_data["storico_saldi"]:
                    if isinstance(modifica, dict) and "tipo_modifica" in modifica and "saldo_aggiunto" in modifica and "data" in modifica:
                        modifica_data = datetime.strptime(modifica["data"], "%Y-%m-%d").date()
                        if modifica["tipo_modifica"] == "Saldo Aggiunto" and data_inizio_formattata <= modifica_data <= data_fine_formattata:
                            saldo_totale += modifica["saldo_aggiunto"]

                saldo_label = tk.Label(slot_frame, text="Saldo: {:.2f}".format(saldo_totale), width=15, anchor="w")
                saldo_label.pack(side=tk.LEFT)

                #Inserimento percentuale fatta su saldo totale
                percentuale_label = tk.Label(slot_frame, text="Percentuale: {:.2f}%".format((float(saldo_totale) / 30000) * 100), width=15, anchor="w")
                percentuale_label.pack(side=tk.LEFT)
            else:
                saldo_label = tk.Label(slot_frame, text="Saldo: N/A", width=15, anchor="w")
                saldo_label.pack(side=tk.LEFT)

                percentuale_label = tk.Label(slot_frame, text="Percentuale: N/A", width=15, anchor="w")
                percentuale_label.pack(side=tk.LEFT)


        numero_scheda_label = tk.Label(slot_frame, text="Numero Scheda: " + slot_data["numero_scheda"], width=25, anchor="w")
        numero_scheda_label.pack(side=tk.LEFT)

        id_macchina_label = tk.Label(slot_frame, text="ID Macchina: " + slot_data["id_macchina"], width=25, anchor="w")
        id_macchina_label.pack(side=tk.LEFT)

        #percentuale_label = tk.Label(slot_frame, text="Percentuale: {:.2f}%".format((float(slot_data["saldo"]) / 30000) * 100), width=15, anchor="w")
        #percentuale_label.pack(side=tk.LEFT)

        aggiungi_saldo_button = tk.Button(slot_frame, text="Aggiungi Saldo", command=lambda sid=slot.id: aggiungi_saldo(sid), width=15)
        aggiungi_saldo_button.pack(side=tk.LEFT)

        modifica_button = tk.Button(slot_frame, text="Modifica", command=lambda sid=slot.id: modifica_slot(sid), width=10)
        modifica_button.pack(side=tk.LEFT)

        elimina_button = tk.Button(slot_frame, text="Elimina", command=lambda sid=slot.id: elimina_slot(sid), width=10)
        elimina_button.pack(side=tk.LEFT)

        storico_button = tk.Button(slot_frame, text="Storico", command=lambda sid=slot.id: mostra_storico(sid), width=10, fg = "red")
        storico_button.pack(side=tk.LEFT)

        # Aggiungi colore personalizzato ai label se presente
        if slot.id in label_colors:
            color = label_colors[slot.id]
            nome_label.config(fg=color.get("nome", "red"))
            ubicazione_label.config(fg=color.get("ubicazione", "black"))
            saldo_label.config(fg=color.get("saldo", "green"))
            numero_scheda_label.config(fg=color.get("numero_scheda", "blue"))
            id_macchina_label.config(fg=color.get("id_macchina", "purple"))
            percentuale_label.config(fg=color.get("percentuale", "black"))
        else:
            # Imposta i colori predefiniti
            nome_label.config(fg="red")
            ubicazione_label.config(fg="black")
            saldo_label.config(fg="green")
            numero_scheda_label.config(fg="blue")
            id_macchina_label.config(fg="purple")

            # Imposta il colore del label "Percentuale" in base alla percentuale di guadagno
            percentuale = (float(slot_data["saldo"]) / 30000) * 100
            if percentuale > 15:
                percentuale_label.config(fg="black")
            else:
                percentuale_label.config(fg="red")

        index += 1
        
    # Imposta lo stato di attivazione/disattivazione dei bottoni di scroll
    scroll_up_button.config(state=tk.NORMAL if scroll_start_index > 0 else tk.DISABLED)
    scroll_down_button.config(state=tk.NORMAL if scroll_start_index + scroll_height < len(slots) else tk.DISABLED)


# Funzione per lo scroll verso l'alto nella visualizzazione
def scroll_up():
    global scroll_start_index
    if scroll_start_index > 0:
        scroll_start_index -= 1
        aggiorna_visualizzazione_slot()

# Funzione per lo scroll verso il basso nella visualizzazione
def scroll_down():
    global scroll_start_index
    if scroll_start_index + scroll_height < len(slots):
        scroll_start_index += 1
        aggiorna_visualizzazione_slot()

# Funzione per mostrare lo storico dei saldi
def mostra_storico(slot_id):
    finestra_storico = tk.Toplevel()
    finestra_storico.title("Storico Saldo")
    finestra_storico.resizable(False, False)  # Disabilita la ridimensionabilità della finestra

    def esc_storico():
        finestra_storico.destroy()

    finestra_width = 290
    finestra_height = 500

    # Calcola le coordinate x e y per centrare la finestra sulla schermata
    screen_width = finestra_storico.winfo_screenwidth()
    screen_height = finestra_storico.winfo_screenheight()
    x = (screen_width // 2) - (finestra_width // 2)
    y = (screen_height // 2) - (finestra_height // 2)

    finestra_storico.geometry("{}x{}+{}+{}".format(finestra_width, finestra_height, x, y))

    # Recupera la slot dal database Firestore
    doc_ref = db.collection(u'slots').document(slot_id)
    slot = doc_ref.get().to_dict()

    # Recupera lo storico delle modifiche al saldo dalla collezione "storico_saldi"
    storico = doc_ref.collection(u'storico_saldi').order_by(u'data_ora', direction=firestore.Query.ASCENDING).get()

    # Crea un widget Canvas per contenere la lista scrollabile
    canvas = tk.Canvas(finestra_storico)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Imposta la lista scrollabile
    lista_storico = tk.Listbox(canvas)

    # Aggiungi il contenuto alla lista
    lista_storico.insert(tk.END, "Data/Ora di Creazione: " + slot["data_e_ora_creazione"])
    lista_storico.insert(tk.END, "Data Selezionata: " + slot["data_selezionata"])
    lista_storico.insert(tk.END, 'Saldo Iniziale: ' + slot.get('saldo_iniziale', 'N/A'))
    lista_storico.insert(tk.END, "Saldo Attuale: " + str(slot["saldo"]))
    lista_storico.insert(tk.END, "Giri Effettuati: " + str(slot["giri_effettuati"]))
    lista_storico.insert(tk.END, "Storico Saldi:")
    lista_storico.insert(tk.END, "-" * 47)  # Puoi personalizzare il numero di caratteri a tua discrezione


    for saldo in storico:
        saldo_data = saldo.to_dict()
        lista_storico.insert(tk.END, "Data/Ora: " + saldo_data["data_ora"])
        lista_storico.insert(tk.END, "Tipo Modifica: " + saldo_data["tipo_modifica"])
        lista_storico.insert(tk.END, "Saldo Aggiunto: " + saldo_data.get("saldo_aggiunto", "N/A"))
        lista_storico.insert(tk.END, "Saldo Precedente: " + saldo_data.get("saldo_prima_modifica", "N/A"))
        lista_storico.insert(tk.END, "Differenza di Saldo: " + saldo_data.get("differenza_saldo", "N/A"))

        # Aggiunta delle etichette per i giri effettuati
        lista_storico.insert(tk.END, "Giri Effettuati Aggiunti: " + saldo_data.get("giri_aggiunti", "N/A"))
        lista_storico.insert(tk.END, "Giri Effettuati Precedenti: " + saldo_data.get("giri_prima_modifica", "N/A"))
        lista_storico.insert(tk.END, "Differenza di Giri Effettuati: " + saldo_data.get("differenza_giri", "N/A"))
        lista_storico.insert(tk.END, "-" * 47)  # Puoi personalizzare il numero di caratteri a tua discrezione

    # Configura il canvas per gestire la scrollbar
    canvas.create_window((0, 0), window=lista_storico, anchor=tk.NW, width=finestra_width, height=finestra_height)

    # Aggiorna la scrollbar
    canvas.configure(scrollregion=canvas.bbox(tk.ALL))

    finestra_storico.bind("<Escape>", lambda event: esc_storico())
    finestra_storico.mainloop()
    
def cancella_storico_slot(slot_id, finestra_storico):
    conferma = messagebox.askyesno("Conferma", "Sei sicuro di voler cancellare lo storico di questa slot?\nQuesta azione è irreversibile.")
    if conferma:
        # Setta il saldo e i giri_effettuati della slot a 0
        db.collection(u'slots').document(slot_id).update({
            u'saldo': 0,
            u'saldo_iniziale': '0',
            u'giri_effettuati': '0'  # Assumendo che 'giri_effettuati' sia rappresentato come stringa
        })

        # Recupera il riferimento alla collezione "storico_saldi" della slot
        storico_ref = db.collection(u'slots').document(slot_id).collection(u'storico_saldi')

        # Cancella tutti i documenti nella collezione "storico_saldi"
        docs = storico_ref.stream()
        for doc in docs:
            doc.reference.delete()

        messagebox.showinfo("Successo", "Storico cancellato con successo")

        finestra_storico.destroy()

        aggiorna_lista_slot()  # Aggiorna la lista delle slot dopo aver cancellato lo storico
        aggiorna_numero_slot()


def verifica_aggiornamenti():
    try:
        # Effettua la richiesta HTTP per ottenere la nuova versione dal repository
        url = "https://raw.githubusercontent.com/Antomell/eurog/main/version.txt"
        response = requests.get(url)
        response.raise_for_status()  # Solleva un'eccezione in caso di status code diverso da 200

        nuova_versione = response.text.strip()

        if nuova_versione == versione_corrente:
            messagebox.showinfo("Aggiornamenti", "Hai già installato la versione più recente.")
        else:
            risposta = messagebox.askyesno("Aggiornamenti", "È disponibile un aggiornamento. Vuoi installarlo?")
            if risposta:
                # Scarica il nuovo script dal repository
                nuovo_script_url = "https://raw.githubusercontent.com/Antomell/eurog/main/script.py"
                response = requests.get(nuovo_script_url)
                response.raise_for_status()  # Solleva un'eccezione in caso di status code diverso da 200

                nuovo_script = response.text

                # Sovrascrivi il vecchio script con il nuovo script
                with open(sys.argv[0], "w") as file:
                    file.write(nuovo_script)

                # Mostro il messaggio di riavvio
                messagebox.showinfo("Aggiornamenti", "Il programma sta per essere riavviato.")

                # Riavvia il programma
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit()

    except requests.RequestException as e:
        messagebox.showerror("Errore", "Errore durante il controllo degli aggiornamenti\n")

def seleziona_data():
    def esc_data():
        finestra_data.destroy()
        ricerca_entry.focus_set()

    def conferma_selezione():
        global data_inizio, data_fine, data_inizio_formattata, data_fine_formattata
        data_inizio = cal_inizio.get_date()
        data_inizio_formattata=data_inizio.strftime("%Y-%m-%d")
        data_fine = cal_fine.get_date()
        data_fine_formattata=data_fine.strftime("%Y-%m-%d")
        finestra_data.destroy()

        # Calcola le statistiche basate sullo storico dei saldi per le date selezionate
        saldo_totale, operazioni_saldo_aggiunto = calcola_statistiche(data_inizio, data_fine)

        # Mostra le statistiche calcolate
        messagebox.showinfo("Statistiche", f"Saldo slots alla data: {saldo_totale:.2f}\nOperazioni totali saldo: {operazioni_saldo_aggiunto}")
        abilita_deseleziona_data()
        aggiorna_visualizzazione_slot()

    finestra_data = tk.Toplevel()
    finestra_data.title("Seleziona Data")

    # Imposta le dimensioni della finestra
    finestra_data_width = 300
    finestra_data_height = 100
    finestra_data.geometry(f"{finestra_data_width}x{finestra_data_height}")

    # Centra la finestra sullo schermo
    finestra_data.update_idletasks()
    screen_width = finestra_data.winfo_screenwidth()
    screen_height = finestra_data.winfo_screenheight()
    x = (screen_width - finestra_data_width) // 2
    y = (screen_height - finestra_data_height) // 2
    finestra_data.geometry(f"+{x}+{y}")

    # Rendi la finestra non resizable
    finestra_data.resizable(False, False)

    today = date.today()

    singola_data_label = tk.Label(finestra_data, text="Seleziona un intervallo di date:")
    singola_data_label.pack()

    cal_inizio = DateEntry(finestra_data, selectmode='day', year=today.year-1, month=today.month, day=today.day, maxdate=today)
    cal_inizio.pack()

    cal_fine = DateEntry(finestra_data, selectmode='day', year=today.year, month=today.month, day=today.day, maxdate=today)
    cal_fine.pack()

    conferma_button = tk.Button(finestra_data, text="Conferma", command=conferma_selezione)
    conferma_button.pack()

    finestra_data.bind("<Escape>", lambda event: esc_data())
    finestra_data.bind("<Return>", lambda event: conferma_selezione())

def aggiorna_numero_slot():
    global numero_slot_label, slots
    numero_slot_label.config(text="Slots Visualizzate in lista: " + str(len(slots)))
    finestra.after(5000, aggiorna_numero_slot)  # Chiama di nuovo la funzione ogni 5 secondi

# Funzione per il calcolo delle statistiche basate sullo storico dei saldi
def calcola_statistiche(data_inizio, data_fine):
    global slots

    saldo_totale = 0
    operazioni_saldo_aggiunto = 0

    for slot in slots:
        doc_ref = db.collection(u'slots').document(slot.id)
        storico = doc_ref.collection(u'storico_saldi').order_by(u'data_ora', direction=firestore.Query.ASCENDING).stream()

        for saldo in storico:
            saldo_data = saldo.to_dict()
            data_operazione = datetime.strptime(saldo_data["data_ora"], "%Y-%m-%d %H:%M:%S").date()

            if data_inizio <= data_operazione <= data_fine:
                saldo_aggiunto = float(saldo_data.get("saldo_aggiunto", 0))
                saldo_totale += saldo_aggiunto

                if saldo_aggiunto > 0:
                    operazioni_saldo_aggiunto += 1

    return saldo_totale, operazioni_saldo_aggiunto

def abilita_deseleziona_data():
    deseleziona_data_button.config(state="normal")

def disabilita_deseleziona_data():
    global data_selezionata,data_inizio,data_fine_formattata,data_fine,data_inizio_formattata
    #Codice da inserire per riportare la lista allo stato di default
    data_selezionata = None
    data_inizio = None
    data_inizio_formattata = None
    data_fine = None
    data_fine_formattata = None
    deseleziona_data_button.config(state="disabled")
    messagebox.showinfo("Data Deselezionata", "Hai deselezionato l'intervallo di date, ora vedrai tutto come se non le avessi proprio selezionate!")
    aggiorna_visualizzazione_slot()
    

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("EUROGAMES S.R.L.")

larghezza_finestra = 800  # Larghezza desiderata della finestra
altezza_finestra = 600  # Altezza desiderata della finestra

larghezza_schermo = finestra.winfo_screenwidth()
altezza_schermo = finestra.winfo_screenheight()

posizione_x = int((larghezza_schermo - larghezza_finestra) / 2)
posizione_y = int((altezza_schermo - altezza_finestra) / 2)

finestra.geometry(f"{larghezza_finestra}x{altezza_finestra}+{posizione_x}+{posizione_y}")
finestra.attributes("-fullscreen", True)
finestra.resizable(False, False)

frame2 = tk.Frame(finestra, padx=5, pady=5)  # Puoi regolare il padding (spazio interno) del frame qui
frame2.pack()

# Carica il logo con dimensioni specifiche
logo_image = PhotoImage(file="/Users/antonio/Desktop/EuroGames/logo.png", width=500, height=200)  # Sostituisci con il percorso del tuo logo e le dimensioni desiderate

# Crea un widget Label per mostrare il logo
logo_label = tk.Label(frame2, image=logo_image)
logo_label.pack(side="top", fill="both", expand="true")

ricerca_label = tk.Label(frame2, text="Cerca: ")
ricerca_label.pack(side=tk.TOP, padx=5)

ricerca_entry = tk.Entry(frame2)
ricerca_entry.pack(side=tk.TOP, padx=5)
ricerca_entry.bind('<KeyRelease>', cerca_slot)  # Aggiunto il binding all'evento KeyRelease

frame1 = tk.Frame(finestra, padx=5, pady=5)  # Puoi regolare il padding (spazio interno) del frame qui
frame1.pack()

aggiungi_button = tk.Button(frame1, text="Aggiungi Slot", command=aggiungi_slot)
aggiungi_button.pack(side=tk.LEFT, padx=20)

seleziona_data_button = tk.Button(frame1, text="Seleziona Data", command=seleziona_data)
seleziona_data_button.pack(side=tk.LEFT, padx=20)

numero_slot_label = tk.Label(frame1, text="Slots Visualizzate in lista: 0")
numero_slot_label.pack(side=tk.LEFT, padx=20)

frame3= tk.Frame(finestra, padx=5, pady=5) 
frame3.pack()

verifica_aggiornamenti_button = tk.Button(frame3, text="Verifica Aggiornamenti", command=verifica_aggiornamenti, fg ="red")
verifica_aggiornamenti_button.pack(side=tk.LEFT, padx=20)

deseleziona_data_button= tk.Button(frame3, text="Deseleziona Data", foreground="red", state="disabled", command=disabilita_deseleziona_data)
deseleziona_data_button.pack(side=tk.RIGHT, padx=20)

scroll_up_button = tk.Button(finestra, text="▲", command=scroll_up)
scroll_up_button.pack()

lista_slot_frame = tk.Frame(finestra)
lista_slot_frame.pack()


scroll_down_button = tk.Button(finestra, text="▼", command=scroll_down)
scroll_down_button.pack()

aggiorna_lista_slot()  # Aggiorna la lista delle slot
aggiorna_numero_slot()


#Inserimento icon programma
finestra.iconbitmap("")
ricerca_entry.focus_set()
finestra.mainloop()