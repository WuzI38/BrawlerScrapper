CREATE DATABASE Brawler;

CREATE TABLE Brawler.Cards (
    id INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(15) NOT NULL,
    image VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Brawler.Commanders (
    id INT AUTO_INCREMENT,
    card_id INT NOT NULL,
    colors VARCHAR(5) NOT NULL,
    decks INT DEFAULT 1,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (card_id) REFERENCES Cards(id)
);

CREATE TABLE Brawler.Decks (
    commander_id INT NOT NULL,
    card_id INT NOT NULL,
    card_count INT DEFAULT 1,
    PRIMARY KEY (commander_id, card_id),
    FOREIGN KEY (commander_id) REFERENCES Commanders(id),
    FOREIGN KEY (card_id) REFERENCES Cards(id)
);

