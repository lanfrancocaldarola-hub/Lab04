class Espositore:
    def __init__(self, codice, nome, cognome):
        self.codice = codice
        self.nome = nome
        self.cognome = cognome

    def __eq__(self, other):
        if isinstance(other, Espositore):
            return self.codice == other.codice
        return False

    def __str__(self):
        return f"{self.codice}: {self.nome} {self.cognome}"


class Stand:
    def __init__(self, codice, superficie, padiglione, prezzo_base):
        self.codice = codice
        self.superficie = float(superficie)
        self.padiglione = int(padiglione)
        self.prezzo_base = float(prezzo_base)
        self.espositore = None  # Riferimento all'espositore associato (None se disponibile)

    @property
    def disponibile(self):
        return self.espositore is None

    def get_prezzo_finale(self):
        """Metodo polimorfico per il calcolo del prezzo finale"""
        return self.prezzo_base

    def __lt__(self, other):
        """Permette l'ordinamento per prezzo crescente (<)"""
        if isinstance(other, Stand):
            return self.get_prezzo_finale() < other.get_prezzo_finale()
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Stand):
            return self.codice == other.codice
        return False

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Standard | {self.superficie:.0f} mq - Padiglione {self.padiglione} - "
                f"Prezzo {self.get_prezzo_finale():.2f}€ - {stato}")


class StandExtraPrese(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, numero_prese):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.numero_prese = int(numero_prese)

    def get_prezzo_finale(self):
        return self.prezzo_base * (1 + 0.07 * self.numero_prese)

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Prese Extra | {self.superficie:.0f} mq - Padiglione {self.padiglione} - "
                f"Prezzo {self.get_prezzo_finale():.2f}€ - Prese aggiuntive: {self.numero_prese} - {stato}")


class StandPremium(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, posizione):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.posizione = posizione

    def get_prezzo_finale(self):
        return self.prezzo_base * 1.30

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self.espositore.codice}"
        return (f"{self.codice}: Premium | {self.superficie:.0f} mq - Padiglione {self.padiglione} - "
                f"Prezzo {self.get_prezzo_finale():.2f}€ - Posizione: {self.posizione} - {stato}")


class LingottoFiere:
    def __init__(self, nome):
        """Inizializza gli attributi e le strutture dati"""
        self._nome = nome
        self.stand_dict = {}
        self.espositori_dict = {}

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, nuovo_nome):
        if nuovo_nome and nuovo_nome.strip():
            self._nome = nuovo_nome.strip()
        else:
            raise ValueError("Il nome non può essere vuoto.")

    def carica_file_dati(self, file_path):
        """Carica i dati (stand ed espositori) dal file CSV"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for riga in f:
                    riga = riga.strip()
                    if not riga:
                        continue

                    campi = [c.strip() for c in riga.split(",")]
                    codice = campi[0]

                    if codice.startswith("ST"):
                        superficie = campi[1]
                        padiglione = campi[2]
                        prezzo_base = campi[3]

                        if len(campi) == 4:
                            nuovo_stand = Stand(codice, superficie, padiglione, prezzo_base)
                        elif len(campi) == 5:
                            valore_extra = campi[4]
                            if valore_extra.isdigit():
                                nuovo_stand = StandExtraPrese(codice, superficie, padiglione, prezzo_base, valore_extra)
                            else:
                                nuovo_stand = StandPremium(codice, superficie, padiglione, prezzo_base, valore_extra)

                        self.stand_dict[codice] = nuovo_stand

                    elif codice.startswith("ES"):
                        nome = campi[1]
                        cognome = campi[2]
                        nuovo_espositore = Espositore(codice, nome, cognome)
                        self.espositori_dict[codice] = nuovo_espositore

        except FileNotFoundError:
            raise FileNotFoundError(f"Impossibile trovare il file: {file_path}")

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        """Associa uno stand a un espositore eseguendo i controlli richiesti"""
        if codice_stand not in self.stand_dict:
            raise ValueError(f"Lo stand {codice_stand} non esiste.")

        if codice_espositore not in self.espositori_dict:
            raise ValueError(f"L'espositore {codice_espositore} non esiste.")

        stand = self.stand_dict[codice_stand]
        espositore = self.espositori_dict[codice_espositore]

        if not stand.disponibile:
            raise ValueError(f"Lo stand {codice_stand} è già stato assegnato.")

        for s in self.stand_dict.values():
            if s.espositore == espositore:
                raise ValueError(f"L'espositore {codice_espositore} ha già uno stand assegnato ({s.codice}).")

        stand.espositore = espositore

    def elenca_espositori(self):
        """Stampa l'elenco degli espositori mostrando l'eventuale stand associato"""
        if not self.espositori_dict:
            print("Nessun espositore registrato.")
            return

        for espositore in self.espositori_dict.values():
            stand_assegnato = None
            for s in self.stand_dict.values():
                if s.espositore == espositore:
                    stand_assegnato = s
                    break

            if stand_assegnato:
                print(f"{espositore} -> Stand assegnato: {stand_assegnato.codice}")
            else:
                print(f"{espositore} -> Nessun uno stand assegnato")

    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista degli stand ordinati per prezzo crescente usando __lt__"""
        lista_stand = list(self.stand_dict.values())
        return sorted(lista_stand)