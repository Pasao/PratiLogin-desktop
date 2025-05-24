# 🚀 PratiLogin - Accesso Semplificato alla Rete Universitaria

Questa è la nuova versione di PratiLogin, un'applicazione desktop progettata per superare le problematiche di connessione alla rete Praticelli dell'Università di Pisa.
⚠️ NOTA: Il programma funziona solo all'interno del campus universitario.

---

## ✨ Obiettivi e Motivazioni

La genesi di PratiLogin risiede in un problema critico e frustrante del captive portal della rete universitaria: la persistente desincronizzazione tra le sessioni utente (lato client) e quelle gestite dal server. Questo "bug" spesso impediva agli studenti di connettersi alla rete per periodi prolungati, talvolta per ore, bloccando di fatto il loro accesso e interrompendo seriamente l'attività accademica.

Questo progetto è stato quindi concepito per fornire una soluzione automatica e semplice a questa barriera tecnica. PratiLogin si propone di rivoluzionare l'esperienza di login degli utenti attraverso:

* **Semplicità d'Uso**: Riduzione delle complicazioni legate al processo di accesso, facilitando un ingresso rapido e senza intoppi nella rete. Il login viene eseguito con un semplice comando. L'utente viene guidato nel setup iniziale, fornendo le credenziali.
* **Robustezza**: Implementazione di strutture e protocolli che garantiscono un funzionamento stabile e resistente agli errori comuni.
* **Fault-Tolerance**: Introduzione di meccanismi che permettono al sistema di operare efficacemente anche in presenza di malfunzionamenti parziali, minimizzando i tempi di inattività.
* **Affidabilità**: Offrire un servizio su cui gli studenti possono contare per accedere alle risorse educative senza interruzioni, migliorando così il flusso di studio e riducendo i disagi causati da sistemi meno affidabili.

## 🌟 Funzionalità Principali

* **Login Automatico**: Tenta la connessione non appena l'applicazione viene avviata (se non sei già connesso).
* **Gestione Sessioni**: Capace di gestire scenari complessi come sessioni lato server bloccate, con opzioni per forzare una nuova autenticazione.
* **Memorizzazione Credenziali Sicura**: Le tue credenziali UNIPI sono salvate in modo sicuro utilizzando il gestore delle credenziali del sistema operativo (es. Windows Credential Manager), non in un file leggibile.
* **Riconnessione Intelligente**: Memorizza l'ultima sede di Praticelli raggiungibile per tentare la riconnessione più velocemente.
* **Interfaccia Semplice**: Un'interfaccia a riga di comando pulita e guidata per tutte le operazioni.
* **Installer Dedicato**: Un file setup.exe per un'installazione professionale su Windows.
* **Logging**: Traccia le attività e gli errori in un file di log per facilitare la diagnosi di eventuali problemi.

## 🤝 Collaborazione e Contributi

Questo progetto è **aperto a contributi**! Ti invitiamo a:

* Segnalare bug o malfunzionamenti
* Aprire issue se trovi problemi o hai domande
* Proporre miglioramenti o nuove funzionalità
* Forkare il progetto, modificarlo e aprire una pull request

Il tuo feedback è fondamentale per migliorare PratiLogin. Più persone interagiscono, testano e discutono del progetto, migliore sarà il risultato finale. Aiutaci a renderlo uno strumento sempre più efficace per tutta la comunità studentesca!

## 💻 Come Farlo Girare (Guida Rapida)

### Installazione su Windows (Consigliata)

1. **Scarica l'Installer**: Visita la pagina delle release del progetto e scarica il file `PratiLogin-X.Y.Z-Setup.exe` (dove X.Y.Z è la versione più recente).
2. **Esegui l'Installer**:

   * Potresti incontrare un avviso da Windows SmartScreen (vedi la sezione "Windows SmartScreen" qui sotto per maggiori dettagli). Clicca su "Ulteriori informazioni" e poi su "Esegui comunque" per procedere.
   * Segui le istruzioni del wizard di installazione. Puoi scegliere la cartella di destinazione (di default `C:\Program Files\PratiLogin`).
   * L'installer creerà automaticamente un collegamento sul Desktop e una voce nel Menu Start.
3. **Primo Avvio dell'App**:

   * Avvia PratiLogin dal collegamento creato sul Desktop o dal Menu Start.
   * Ti verrà richiesto di inserire il tuo username e la password UNIPI. Queste credenziali verranno salvate in modo sicuro nel gestore delle credenziali del sistema operativo.
   * L'applicazione tenterà automaticamente il login.

### Esecuzione come Script Python (per Sviluppatori / Utenti Avanzati)

Se non vuoi utilizzare l'installer o desideri contribuire allo sviluppo, puoi eseguire l'applicazione direttamente come script Python:

1. **Clona il Repository**:

```bash
git clone https://github.com/Pasao/PratiLogin-desktop.git
cd PratiLogin-desktop
```

2. **Crea un Ambiente Virtuale (Consigliato)**:

```bash
python -m venv venv
.\venv\Scripts\activate   # Su Windows
source venv/bin/activate  # Su macOS/Linux
```

3. **Installa le Dipendenze**:

```bash
pip install -r requirements.txt
```

4. **Esegui lo Script**:

```bash
python pratilogin_main.py
```

## ⚠️ Note su Windows SmartScreen

Al primo avvio dell'installer (`PratiLogin-X.Y.Z-Setup.exe`) e/o dell'eseguibile principale (`PratiLogin.exe`), Windows Defender SmartScreen potrebbe mostrare un avviso di sicurezza (es. "Impedita l'esecuzione di un'app non riconosciuta").

Questo accade perché l'applicazione è sviluppata da un autore indipendente e non è firmata digitalmente con un certificato di code signing commerciale (che ha un costo annuale significativo). È un comportamento standard per software non ampiamente diffuso o non firmato.

### Per procedere in sicurezza:

* Nell'avviso di SmartScreen, clicca su "Ulteriori informazioni" (o "More info").
* Apparirà un nuovo pulsante "Esegui comunque" (o "Run anyway"). Cliccalo.

Questa procedura è sicura **se hai scaricato l'installer dalla fonte ufficiale del progetto (questo repository GitHub)**.

## 🛠️ Tecnologie Utilizzate

* **Python**: Linguaggio di programmazione principale.
* **requests**: Per le richieste HTTP alla rete Praticelli.
* **colorama**: Per i messaggi colorati nella console, migliorando la leggibilità.
* **keyring**: Per salvare le credenziali in modo sicuro nel gestore credenziali del sistema operativo.
* **winshell & pywin32**: (Windows-specifico) Utilizzato dall'installer per la gestione di shortcut e percorsi (tramite lazy loading).
* **PyInstaller**: Per creare l'eseguibile auto-contenuto (cartella `--onedir`).
* **Inno Setup**: Per creare l'installer professionale (`setup.exe`) su Windows.

## 🧪 Test e Compatibilità

Questa applicazione è stata sviluppata e testata principalmente sui seguenti sistemi operativi:

* Windows 10
* Windows 11

L'installer (`setup.exe`) è progettato per Windows.

## 🗺️ Roadmap e To-Do List

* [x] Spiegare ulteriormente le ragioni del blocco di Windows SmartScreen
* [ ] Implementare un Installer per macOS e Linux
* [ ] Documentazione Avanzata per sviluppatori e utenti esperti
* [ ] Miglioramenti UI/UX (interfaccia CLI e possibile GUI futura)

## ⚠️ Disclaimer

Questo script automatizza la procedura di login alla rete Praticelli tramite richieste HTTP osservabili normalmente durante la navigazione.  
Le informazioni sono state ottenute analizzando il traffico del proprio browser durante l’autenticazione, senza violare la privacy di terzi né bypassare misure di sicurezza.
Sono stati usati strumenti come BurpSuite e Wireshark per comprendere come fossero eseguite le richieste.

Il codice è pensato per l’uso personale da parte di studenti con accesso autorizzato alla rete.  
Non incoraggia né abilita comportamenti illeciti.
