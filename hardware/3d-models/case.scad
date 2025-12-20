/*
 * Volume Be Gone - Carcasa para Raspberry Pi 4
 *
 * Author: Francisco Ortiz Rojas
 *         Ingeniero Electronico
 *         francisco.ortiz@marfinex.com
 *
 * Version: 2.1
 * Date: Diciembre 2025
 *
 * Uso:
 *   openscad case.scad                    # Abrir en GUI
 *   openscad -o case.stl case.scad        # Exportar STL
 *   openscad -o case_lid.stl -D "part=\"lid\"" case.scad  # Solo tapa
 *   openscad -o case_base.stl -D "part=\"base\"" case.scad # Solo base
 */

// ============================================
// PARAMETROS CONFIGURABLES
// ============================================

// Que parte renderizar: "all", "base", "lid"
part = "all";

// Tolerancia de impresion (ajustar segun impresora)
tolerance = 0.3;

// Grosor de paredes
wall = 2.5;

// Resolucion de circulos
$fn = 50;

// ============================================
// DIMENSIONES RASPBERRY PI 4
// ============================================

// PCB dimensions
rpi_length = 85;
rpi_width = 56;
rpi_height = 17;  // Altura con componentes

// Posiciones de montaje (desde esquina inferior izquierda)
rpi_hole_diameter = 2.7;
rpi_holes = [
    [3.5, 3.5],
    [3.5 + 58, 3.5],
    [3.5, 3.5 + 49],
    [3.5 + 58, 3.5 + 49]
];

// Altura de los standoffs
standoff_height = 5;
standoff_outer = 6;

// ============================================
// DIMENSIONES PUERTOS RPi4 (Verificado con specs oficiales)
// Referencia: datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf
// ============================================

// USB-C Power (lado corto, desde esquina SD card)
usbc_width = 9;
usbc_height = 3.5;
usbc_pos = 11.2;  // Centro a 11.2mm desde esquina

// Micro HDMI x2 (lado corto)
hdmi_width = 7.8;
hdmi_height = 3.5;
hdmi1_pos = 26.0;   // HDMI0 - centro a 26mm desde esquina
hdmi2_pos = 39.5;   // HDMI1 - centro a 39.5mm desde esquina

// Audio jack 3.5mm (lado corto)
audio_diameter = 7;
audio_pos = 53.5;   // Centro a 53.5mm desde esquina

// Ethernet RJ45 (lado largo, desde esquina audio)
eth_width = 16;
eth_height = 14;
eth_pos = 10.25;    // Centro a 10.25mm desde esquina

// USB 3.0 x2 apilados (lado largo, azules, junto a ethernet)
usb3_width = 13.5;
usb3_height = 16;
usb3_pos = 29;      // Centro a 29mm desde esquina

// USB 2.0 x2 apilados (lado largo, negros, mas lejos de ethernet)
usb2_width = 13.5;
usb2_height = 16;
usb2_pos = 47;      // Centro a 47mm desde esquina

// ============================================
// DIMENSIONES PANTALLA OLED SSD1306 0.96" 128x64
// Nota: Las medidas pueden variar segun fabricante. Mide tu modulo!
// Referencia: Modulo generico 4-pin I2C (mas comun)
// ============================================

// PCB del modulo OLED
oled_pcb_width = 27.3;      // Ancho PCB (puede ser 26-28mm)
oled_pcb_height = 27.8;     // Alto PCB (puede ser 27-28mm)
oled_pcb_thickness = 1.2;   // Grosor PCB

// Area visible del display
oled_screen_width = 21.7;   // Ancho area visible
oled_screen_height = 10.8;  // Alto area visible
oled_screen_offset_x = 2.8; // Offset desde borde izquierdo del PCB
oled_screen_offset_y = 4.5; // Offset desde borde inferior (lado pines)

// Orificios de montaje (4 esquinas)
oled_hole_diameter = 2.2;   // Diametro para tornillos M2
oled_hole_spacing_x = 23.0; // Distancia horizontal entre centros
oled_hole_spacing_y = 23.5; // Distancia vertical entre centros
oled_hole_edge_offset = 2.0; // Distancia del centro del orificio al borde

// Posiciones de orificios (desde esquina inferior izquierda del PCB)
oled_holes = [
    [oled_hole_edge_offset, oled_hole_edge_offset],
    [oled_pcb_width - oled_hole_edge_offset, oled_hole_edge_offset],
    [oled_hole_edge_offset, oled_pcb_height - oled_hole_edge_offset],
    [oled_pcb_width - oled_hole_edge_offset, oled_pcb_height - oled_hole_edge_offset]
];

// Alias para compatibilidad
oled_width = oled_pcb_width;
oled_height = oled_pcb_height;
oled_mounting_holes = oled_hole_diameter;

// ============================================
// DIMENSIONES ENCODER KY-040
// ============================================

encoder_shaft_diameter = 7;
encoder_body_diameter = 12;
encoder_nut_diameter = 10;  // Para el hueco hexagonal

// ============================================
// DIMENSIONES CARCASA
// ============================================

// Espacio interno adicional
clearance = 3;

// Dimensiones internas
inner_length = rpi_length + clearance * 2;
inner_width = rpi_width + clearance * 2;
inner_height = rpi_height + standoff_height + clearance + 15;  // +15 para OLED y cables

// Dimensiones externas
outer_length = inner_length + wall * 2;
outer_width = inner_width + wall * 2;
outer_height = inner_height + wall * 2;

// Altura de la base (donde va la RPi)
base_height = standoff_height + rpi_height + wall + 5;

// Altura de la tapa
lid_height = outer_height - base_height + wall;

// ============================================
// MODULOS
// ============================================

// Standoff para montaje de RPi
module standoff(h, outer_d, inner_d) {
    difference() {
        cylinder(h=h, d=outer_d);
        cylinder(h=h+1, d=inner_d);
    }
}

// Hueco rectangular redondeado
module rounded_slot(w, h, depth, r=1) {
    translate([0, 0, -0.1])
    linear_extrude(depth + 0.2)
    offset(r=r)
    offset(r=-r)
    square([w, h], center=true);
}

// Ventilacion (patron de ranuras)
module vent_slots(length, width, slot_width=2, slot_spacing=4, depth=wall+1) {
    num_slots = floor(length / (slot_width + slot_spacing));
    start_x = -(num_slots - 1) * (slot_width + slot_spacing) / 2;

    for (i = [0:num_slots-1]) {
        translate([start_x + i * (slot_width + slot_spacing), 0, 0])
        rounded_slot(slot_width, width, depth, r=slot_width/2);
    }
}

// Caja basica con esquinas redondeadas
module rounded_box(l, w, h, r=3) {
    translate([r, r, 0])
    minkowski() {
        cube([l - 2*r, w - 2*r, h/2]);
        cylinder(r=r, h=h/2);
    }
}

// ============================================
// BASE DE LA CARCASA
// ============================================

module case_base() {
    difference() {
        // Caja exterior
        rounded_box(outer_length, outer_width, base_height, r=3);

        // Hueco interior
        translate([wall, wall, wall])
        rounded_box(inner_length, inner_width, base_height, r=2);

        // === PUERTOS LADO USB-C (frontal, Y=0) ===
        // Posiciones medidas desde esquina PCB + clearance + wall

        // USB-C Power (centro a 11.2mm desde esquina)
        translate([wall + clearance + usbc_pos, -1, wall + standoff_height])
        rotate([-90, 0, 0])
        rounded_slot(usbc_width + tolerance*2, usbc_height + tolerance*2, wall+2);

        // Micro HDMI 0 (centro a 26mm desde esquina)
        translate([wall + clearance + hdmi1_pos, -1, wall + standoff_height])
        rotate([-90, 0, 0])
        rounded_slot(hdmi_width + tolerance*2, hdmi_height + tolerance*2, wall+2);

        // Micro HDMI 1 (centro a 39.5mm desde esquina)
        translate([wall + clearance + hdmi2_pos, -1, wall + standoff_height])
        rotate([-90, 0, 0])
        rounded_slot(hdmi_width + tolerance*2, hdmi_height + tolerance*2, wall+2);

        // Audio jack (centro a 53.5mm desde esquina)
        translate([wall + clearance + audio_pos, -1, wall + standoff_height + 2])
        rotate([-90, 0, 0])
        cylinder(d=audio_diameter + tolerance*2, h=wall+2);

        // === PUERTOS LADO ETHERNET/USB (lado largo, X=max) ===
        // Posiciones medidas desde esquina opuesta al GPIO

        // Ethernet RJ45 (centro a 10.25mm desde esquina)
        translate([outer_length - wall - 1, wall + clearance + eth_pos, wall + standoff_height])
        rotate([0, 90, 0])
        rotate([0, 0, 90])
        rounded_slot(eth_width + tolerance*2, eth_height + tolerance*2, wall+2);

        // USB 3.0 x2 apilados (centro a 29mm desde esquina)
        translate([outer_length - wall - 1, wall + clearance + usb3_pos, wall + standoff_height])
        rotate([0, 90, 0])
        rotate([0, 0, 90])
        rounded_slot(usb3_width + tolerance*2, usb3_height + tolerance*2, wall+2);

        // USB 2.0 x2 apilados (centro a 47mm desde esquina)
        translate([outer_length - wall - 1, wall + clearance + usb2_pos, wall + standoff_height])
        rotate([0, 90, 0])
        rotate([0, 0, 90])
        rounded_slot(usb2_width + tolerance*2, usb2_height + tolerance*2, wall+2);

        // === VENTILACION INFERIOR ===
        translate([outer_length/2, outer_width/2, -0.1])
        vent_slots(outer_length - 20, 30, slot_width=3, slot_spacing=5);

        // === VENTILACION LATERAL (lado sin puertos) ===
        translate([outer_length/2, outer_width - wall/2, base_height/2])
        rotate([90, 0, 0])
        vent_slots(outer_length - 30, base_height - 15, slot_width=2, slot_spacing=4);

        // === RANURA PARA TARJETA SD (lado posterior) ===
        translate([wall + clearance + 2, outer_width - wall - 1, wall + standoff_height - 2])
        rotate([90, 0, 0])
        rounded_slot(14, 3, wall+2);
    }

    // === STANDOFFS PARA RASPBERRY PI ===
    for (hole = rpi_holes) {
        translate([wall + clearance + hole[0], wall + clearance + hole[1], wall])
        standoff(standoff_height, standoff_outer, rpi_hole_diameter);
    }

    // === GUIAS PARA LA TAPA ===
    lip_height = 3;
    lip_width = 1.5;

    difference() {
        translate([wall - lip_width, wall - lip_width, base_height - lip_height])
        rounded_box(inner_length + lip_width*2, inner_width + lip_width*2, lip_height, r=2);

        translate([wall, wall, base_height - lip_height - 0.1])
        rounded_box(inner_length, inner_width, lip_height + 1, r=2);
    }
}

// ============================================
// TAPA DE LA CARCASA
// ============================================

module case_lid() {
    difference() {
        union() {
            // Tapa principal
            rounded_box(outer_length, outer_width, lid_height, r=3);

            // Labio interior para encajar
            translate([wall + tolerance, wall + tolerance, -2])
            rounded_box(inner_length - tolerance*2, inner_width - tolerance*2, 2 + 0.1, r=1.5);
        }

        // Hueco interior
        translate([wall, wall, -0.1])
        rounded_box(inner_length, inner_width, lid_height - wall + 0.1, r=2);

        // === HUECO PARA PANTALLA OLED ===
        // Posicion: centrado en X, hacia el frente
        oled_x = outer_length/2;
        oled_y = 25;

        // Hueco para la pantalla visible
        translate([oled_x, oled_y, lid_height - wall - 0.1])
        rounded_slot(oled_screen_width + 1, oled_screen_height + 1, wall + 1, r=1);

        // Hueco para el modulo completo (mas profundo)
        translate([oled_x, oled_y, lid_height - wall - 3])
        rounded_slot(oled_width + tolerance*2, oled_height + tolerance*2, 4, r=1);

        // === HUECO PARA ENCODER ===
        // Posicion: lado derecho de la tapa
        encoder_x = outer_length - 20;
        encoder_y = outer_width/2;

        // Hueco para el eje
        translate([encoder_x, encoder_y, lid_height - wall - 0.1])
        cylinder(d=encoder_shaft_diameter + tolerance*2, h=wall + 1);

        // Hueco para la tuerca de montaje
        translate([encoder_x, encoder_y, lid_height - wall - 2])
        cylinder(d=encoder_nut_diameter + tolerance, h=3, $fn=6);

        // === VENTILACION SUPERIOR ===
        // Ranuras de ventilacion sobre la CPU
        translate([30, outer_width/2, lid_height - wall/2])
        vent_slots(40, 25, slot_width=2, slot_spacing=4);

        // === TEXTO/LOGO ===
        translate([outer_length/2, outer_width - 12, lid_height - 0.5])
        linear_extrude(1)
        text("Volume Be Gone", size=5, halign="center", valign="center");

        translate([outer_length/2, outer_width - 18, lid_height - 0.5])
        linear_extrude(1)
        text("v2.1", size=3, halign="center", valign="center");
    }
}

// ============================================
// RENDERIZADO
// ============================================

if (part == "base") {
    case_base();
} else if (part == "lid") {
    case_lid();
} else {
    // Mostrar ambas partes separadas para visualizacion
    case_base();

    translate([0, 0, base_height + 10])
    case_lid();
}

// ============================================
// INFORMACION DE IMPRESION
// ============================================

/*
 * PARAMETROS DE IMPRESION RECOMENDADOS:
 *
 * - Material: PLA o PETG
 * - Layer height: 0.2mm
 * - Infill: 20-30%
 * - Paredes: 3 perimetros
 * - Soportes: SI (para los puertos USB/Ethernet)
 * - Orientacion:
 *     - Base: boca arriba (como se ve)
 *     - Tapa: boca abajo (invertida)
 *
 * TIEMPO ESTIMADO:
 * - Base: ~2-3 horas
 * - Tapa: ~1-2 horas
 *
 * COMANDOS PARA EXPORTAR:
 *
 * # Exportar base
 * openscad -o case_base.stl -D 'part="base"' case.scad
 *
 * # Exportar tapa
 * openscad -o case_lid.stl -D 'part="lid"' case.scad
 *
 * # Exportar todo junto (para visualizar)
 * openscad -o case_complete.stl case.scad
 */
