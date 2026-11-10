-- Esquema para MySQL 8 — Gestor de prospectos de seguros
CREATE DATABASE IF NOT EXISTS prospectos_seguros CHARACTER SET utf8mb4;
USE prospectos_seguros;

CREATE TABLE IF NOT EXISTS prospecto (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    telefono      VARCHAR(15),
    correo        VARCHAR(100),
    origen        ENUM('Facebook','Instagram','TikTok','WhatsApp','Referido','Otro') NOT NULL DEFAULT 'Otro',
    etapa         ENUM('Nuevo','Contactado','Cotizado','Cerrado','Perdido') NOT NULL DEFAULT 'Nuevo',
    fecha_alta    DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE IF NOT EXISTS vehiculo (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    prospecto_id  INT NOT NULL,
    tipo          ENUM('Auto','Moto') NOT NULL,
    marca         VARCHAR(40) NOT NULL,
    modelo        VARCHAR(40) NOT NULL,
    anio          SMALLINT NOT NULL,
    FOREIGN KEY (prospecto_id) REFERENCES prospecto(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cotizacion (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id   INT NOT NULL,
    cobertura     ENUM('Responsabilidad Civil','Limitada','Amplia','Premium') NOT NULL,
    prima_anual   DECIMAL(10,2) NOT NULL CHECK (prima_anual > 0),
    fecha         DATE NOT NULL DEFAULT (CURRENT_DATE),
    aceptada      BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculo(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seguimiento (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    prospecto_id    INT NOT NULL,
    fecha_programada DATE NOT NULL,
    nota            VARCHAR(255),
    hecho           BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (prospecto_id) REFERENCES prospecto(id) ON DELETE CASCADE
);

CREATE INDEX idx_prospecto_etapa ON prospecto(etapa);
CREATE INDEX idx_seguimiento_fecha ON seguimiento(fecha_programada, hecho);

-- Vista: embudo de ventas por etapa
CREATE OR REPLACE VIEW v_embudo AS
SELECT etapa, COUNT(*) AS total
FROM prospecto
GROUP BY etapa;

-- Vista: efectividad por red social (tasa de cierre)
CREATE OR REPLACE VIEW v_efectividad_origen AS
SELECT origen,
       COUNT(*) AS prospectos,
       SUM(etapa = 'Cerrado') AS cerrados,
       ROUND(100 * SUM(etapa = 'Cerrado') / COUNT(*), 1) AS tasa_cierre_pct
FROM prospecto
GROUP BY origen
ORDER BY tasa_cierre_pct DESC;
