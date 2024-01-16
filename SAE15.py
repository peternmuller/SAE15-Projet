#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Auteurs : LE TOUZÉ Matthieu, MULLER Peter, CUSTODIO Shawn
# Date : 16/01/2024
# ---------------------------------------------------------------------------
"""
Projet SAÉ15 - Traitement des données
Projet n°1 : aider le secrétariat à contacter un vacataire
Script Python pour l'importation, le traitement et la visualisation des données du fichier ADECal.ics
au format CSV et pour la génération d'un frise chronologique au format PNG.
"""
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import csv
from matplotlib.pyplot import annotate, figure, plot, axis, savefig, arrow, title
from datetime import datetime, timedelta
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pré-traitement
# ---------------------------------------------------------------------------
def importation(fichier):
    """
    Cette fonction importe les données d'un fichier spécifié et les organise dans une liste
    (une ligne = une liste)
    """
    liste = []

    with open(fichier, newline='', encoding="UTF-8") as file:
        for ligne in file:
            # Vérifie si la ligne n'est pas vide et commence par un espace
            if ligne != "" and ligne[0] == " ":
                liste.append(" " + ligne.strip())  # Ajoute la ligne avec un espace au début à la liste et supprime les espaces inutiles à gauche et à droite de la ligne
            else:
                liste.append(ligne.strip())  # Ajoute la ligne sans espace au début à la liste

    return liste


def rassemblement(liste):
    """Cette fonction rassemble les listes communes à un même événement (un événement = une liste de liste)"""
    liste_event = []
    evenement = []

    for ligne in liste:
        if "BEGIN:VEVENT" == ligne:
            evenement = []  # Commence un nouvel événement en initialisant une nouvelle liste
        elif "END:VEVENT" == ligne:
            liste_event.append(evenement)  # Ajoute l'événement à la liste principale
        evenement.append(ligne)  # Ajoute la ligne à l'événement en cours

    # Supprime la dernière ligne de la dernière sous-liste (correspondant à "END:VEVENT")
    del liste_event[-1][-1]

    return liste_event


def organisation(liste):
    """
    Cette fonction organise les détails des événements en une liste propre
    (retrait des titres, réglage des problèmes de sauts de lignes)
    """
    liste_event = []

    for evenement in liste:
        event_propre = []

        for detail in evenement:
            # Vérifie si la ligne n'est pas une balise de début/fin et n'est pas vide
            if detail != "BEGIN:VEVENT" and detail != "END:VEVENT" and detail != "":
                detail = detail.replace("\\n", " ")  # Remplace le saut de ligne par un espace
                if detail[0] == " ":
                    # Ajoute le détail à la ligne précédente s'il commence par un espace
                    event_propre[-1] += detail.strip()
                else:
                    # Ajoute un nouveau détail à la liste si la ligne ne commence pas par un espace
                    event_propre.append(detail[detail.find(":") + 1:].strip())

        liste_event.append(event_propre)

    return liste_event


def exportation(nom, champs, liste):
    """Cette fonction exporte une liste de données dans un fichier CSV avec les champs spécifiés"""
    with open(nom, 'w', newline='', encoding="UTF-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(champs)  # Écrit les en-têtes de colonnes dans le fichier CSV
        csvwriter.writerows(liste)  # Écrit les données de la liste dans le fichier CSV

liste_event = organisation(rassemblement(importation("ADECal.ics")))
exportation("ADECal.csv", ["DTSTAMP", "DTSTART", "DTEND", "SUMMARY", "LOCATION", "DESCRIPTION", "UID", "CREATED", "LAST-MODIFIED", "SEQUENCE"], liste_event)
print("\nLe fichier ADECal.csv a été généré\n")

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Traitement
# ---------------------------------------------------------------------------
def creation_liste_cours(liste):
    """Cette fonction prend une liste de données de cours brut et crée une nouvelle liste de cours formatée"""
    liste_cours = []

    for ligne in liste:

        # Extraction de la date et de l'heure à partir de la chaîne de date
        jour = ligne[1][6:8] + "/" + ligne[1][4:6]+"/" + ligne[1][0:4]
        heure = ligne[1][9:11] + "h" + ligne[1][11:13]

        nom = ""
        ligne_prof = ligne[5][:ligne[5].find("(")].strip().split(" ")

        for element in ligne_prof:
            # Filtre les éléments indésirables et de longueur suffisante pour être considérés comme le nom du professeur
            if ("TD" not in element) and ("RT1" not in element) and ("RT2" not in element) and ("LP" not in element) and ("GSIE" not in element) and ("Apprentissage" not in element) and ("Réunion/Evènement" not in element) and (len(element) >= 3):
                if nom == "":
                    nom = element
                else:
                    nom = nom + " " + element

        liste_cours.append([jour, heure, ligne[3], nom])  # Ajout de la liste du cours à la liste principale

    return liste_cours


def filtre(liste):
    """Cette fonction filtre une liste de cours en fonction des titulaires spécifiés"""
    titulaires = ["CARTIER ANNA", "DEPREZ JEAN-LUC", "MANSOURI ALAMIN", "MARCEL SEVERINE", "NECTOUX ANTOINE", "PETITPRE KAREEN", "ROY MICHAEL", "VIOIX JEAN-BAPTISTE", "ZIMMER CHRISTINE", ""]
    nvl_liste = []

    for ligne in liste:
        if ligne[3] not in titulaires:  # Vérifie si le titulaire n'est pas dans la liste spécifiée
            if ligne[3].count(" ") > 2:  # Vérifie si le nom du titulaire contient plus de deux espaces (au moins trois parties)
                nom = ligne[3].split()
                for i in range(len(nom) - 1):
                    # Vérifie si la combinaison de deux parties du nom n'est pas dans la liste des titulaires
                    if i % 2 == 0 and (nom[i] + " " + nom[i + 1]) not in titulaires:
                        nvl_liste.append(ligne[0:2] + [nom[i] + " " + nom[i + 1]])
            else:
                nvl_liste.append(ligne)  # Ajoute la ligne à la nouvelle liste si les conditions ne sont pas remplies

    return sorted(nvl_liste, key=lambda ligne: ligne[0][6:] + ligne[0][3:5] + ligne[0][:2] + ligne[1][:2] + ligne[1][2:]) 


date_entree = input("Entrer une date (JJ/MM/AAAA) : ")
while date_entree[6:] + date_entree[3:5] + date_entree[:2] > filtre(creation_liste_cours(liste_event))[-1][0][6:] + filtre(creation_liste_cours(liste_event))[-1][0][3:5] + filtre(creation_liste_cours(liste_event))[-1][0][:2]:
    print("Il n'y a pas de cours apres cette date. La date doit être antérieure au", filtre(creation_liste_cours(liste_event))[-1][0])
    date_entree = input("Entrer une date (JJ/MM/AAAA) : ")

def traitement(liste, date_entree):
    """Cette fonction effectue un traitement sur une liste de cours en fonction de la date d'entrée fournie"""
    post_envent = []  # Liste des cours postérieurs à la date d'entrée
    liste_nom = []  # Liste des noms de titulaires déjà traités
    liste_finale = []  # Liste finale des cours traités

    # Filtre les cours postérieurs à la date d'entrée
    for ligne in liste:
        if ligne[0][6:] + ligne[0][3:5] + ligne[0][:2] > date_entree[6:] + date_entree[3:5] + date_entree[:2]:
            post_envent.append(ligne)

    # Trie les cours filtrés par date et sélectionne uniquement le premier cours de chaque titulaire
    for event in post_envent:
        if event[3] not in liste_nom:
            liste_nom.append(event[3])
            liste_finale.append(event)
    
    return liste_finale

liste_finale = traitement(filtre(creation_liste_cours(liste_event)),date_entree)

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Affichage des résultats
# ---------------------------------------------------------------------------
def affichage_liste(liste):
    """Cette fonction affiche les informations sur les cours traités dans la liste"""
    for event in liste:
        print("Le prochain cours de l'enseignant", event[3], "a lieu le", event[0], "à", event[1], "pour un cours intitulé", event[2])


def exportation_frise(liste, date_entree):
    """Cette fonction génère une frise chronologique illustrant les cours programmés pour chaque enseignant"""
    liste_dates = []
    liste_noms = []

    # Crée une liste de dates uniques et une liste correspondante de noms d'enseignants avec les cours associés
    for ligne in liste:
        if datetime.strptime(ligne[0], "%d/%m/%Y") not in liste_dates:
            liste_dates.append(datetime.strptime(ligne[0], "%d/%m/%Y"))
            liste_noms.append(ligne[3] + " (" + ligne[2] + " à "+ligne[1] + ")")
        else:
            liste_noms[-1] = liste_noms[-1] + "\n" + ligne[3] + " (" + ligne[2] + ")"

    ordonnee = [len(liste_dates) - i for i in range(len(liste_dates))]

    figure(figsize=(16, 9))

    # Trace une ligne horizontale représentant le temps
    arrow(liste_dates[0], 0, (liste_dates[-1] - liste_dates[0] + timedelta(days=3)).days*1.5, 0, head_width=len(liste_dates)/10, head_length=(liste_dates[-1] - liste_dates[0] + timedelta(days=1)).days*0.05, linewidth=20, color="c")

    couleurs = ["b", "g", "r", "c", "m", "y"] * 3

    # Trace des lignes pour chaque date avec des cercles pour chaque enseignant et ajoute des annotations pour chaque enseignant avec les cours associés et les dates
    for i, date in enumerate(liste_dates):
        plot([liste_dates[i]] * 3, [ordonnee[i], 0, -(ordonnee[i] % 5) - 1], couleurs[ordonnee[i] - 1] + "-o")
        x = date + max([timedelta((liste_dates[-1] - liste_dates[0]).days * 0.01), timedelta(1) * 0.05])
        annotate(liste_noms[i], xy=[ x, ordonnee[i]], fontsize=7)
        annotate(str(liste_dates[i].date())[8:10] + "/" + str(liste_dates[i].date())[5:7] + "/" + str(liste_dates[i].date())[0:4], 
                 xy=[ x, -(ordonnee[i] % 5) - 1], verticalalignment="top", fontsize=7)

    # Désactive l'affichage des axes sur la figure
    axis("off")
    
    title("Date de la prochaines intervention des vacataires à compté du " + date_entree)
    # Sauvegarde la frise chronologique en tant qu'image PNG
    savefig("vacataire_" + date_entree.replace("/", "-") + ".png", dpi=300)

# Affiche un message indiquant que les fichiers ont été générés avec succès
print("\nLes enseignants vacataires intervenant encore dans l’établissement après la date saisie sont donnés dans les fichiers générés suivants :\n")
# Exporte les résultats dans un fichier CSV
exportation("vacataire_" + date_entree.replace("/", "-") + ".csv", ["Date", "Heure", "Cours", "Vacataire"], liste_finale)
print("        - vacataire_" + date_entree.replace('/', '-') + ".csv (Tableau)")
exportation_frise(liste_finale, date_entree)
print("        - vacataire_" + date_entree.replace('/', '-') + ".png (Frise chronologique)")