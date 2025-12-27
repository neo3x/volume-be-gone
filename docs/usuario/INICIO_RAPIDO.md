# Inicio Rápido - Volume Be Gone

## 5 Minutos para Empezar

---

## Requisitos Previos

- Raspberry Pi con sistema operativo instalado
- Conexión a internet (solo para instalación)
- Los componentes conectados (micrófono, pantalla, encoder)

---

## Paso 1: Descargar

```bash
cd ~
git clone https://github.com/neo3x/volume-be-gone.git
cd volume-be-gone
```

---

## Paso 2: Instalar

```bash
sudo bash scripts/install.sh
```

Espera ~10 minutos. Toma un café ☕

---

## Paso 3: Reiniciar

```bash
sudo reboot
```

---

## Paso 4: Probar

```bash
cd ~/volume-be-gone
./start.sh
```

---

## Paso 5: ¡Listo!

Deberías ver la pantalla funcionando:

```
┌──────────────────────┐
│ VOL: ▓▓▓▓░░░░ 65 dB  │
│ LIM: ████████ 75 dB  │
│ Equipos: 2   [AUTO]  │
└──────────────────────┘
```

---

## Controles Básicos

| Acción | Cómo hacerlo |
|--------|--------------|
| Subir límite | Gira la perilla → derecha |
| Bajar límite | Gira la perilla → izquierda |
| Guardar | Presiona la perilla |

---

## ¿Quieres control desde el celular?

```bash
sudo bash scripts/setup_ap.sh
```

Luego conecta a la red **VolumeBeGone** (contraseña: `begone2025`) y abre `http://192.168.4.1:5000`

---

## ¿Problemas?

Ver el [Manual de Usuario](MANUAL_USUARIO.md) para ayuda detallada.

---

*¡Disfruta tu nueva tranquilidad!* 🎧🔇
