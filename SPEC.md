# SPEC.md - Landing Page Cita Previa Padrón Leganés

## 1. Project Overview

**Project Name:** Cita Previa Padrón Leganés - Landing Page

**Project Type:** Single-page website (landing page)

**Core Functionality:** Landing page de registro donde los vecinos de Leganés pueden inscribirse para recibir notificaciones automáticas cuando haya citas disponibles en el servicio de padrón del Ayuntamiento de Leganés.

**Target Users:** Vecinos de Leganés que necesitan solicitar cita previa para trámites de padrón (cambios de domicilio, empadronamiento, etc.) y no encuentran citas disponibles en la web oficial.

**Target Web:** https://intraweb.leganes.org/CitaPrevia/

---

## 2. UI/UX Specification

### 2.1 Layout Structure

**Page Sections:**
1. **Header** - Logo/título del servicio
2. **Hero Section** - Título attractivo + descripción breve del servicio
3. **Form Section** - Formulario de registro con todos los campos
4. **Features Section** - Explicación de cómo funciona el servicio
5. **Footer** - Información de contacto y copyright

**Responsive Breakpoints:**
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

**Max Content Width:** 1200px

**Layout:**
- Single column en móvil
- Centrado con max-width en desktop
- Padding interno: 24px (móvil), 48px (desktop)

### 2.2 Color Palette

**Primary Color - Azul Ayuntamiento Leganés:**
- Primary: `#0059A8` (azul corporativo Leganés)
- Primary Dark: `#003D73` (hover states)
- Primary Light: `#E8F1FA` (fondos sutiles)

**Neutral Colors:**
- White: `#FFFFFF`
- Background: `#F5F7FA`
- Text Primary: `#1A1A2E`
- Text Secondary: `#5A6170`
- Border: `#D1D9E6`
- Gray Light: `#E5E9F0`

**Accent Colors:**
- Success: `#10B981`
- Error: `#EF4444`
- Warning: `#F59E0B`

**Contrast Ratios:**
- Primary on White: 7.2:1 (AAA compliant)
- Text Primary on Background: 12.5:1 (AAA compliant)
- Text Secondary on Background: 6.8:1 (AA compliant)

### 2.3 Typography

**Font Family:**
- Headings: `"Montserrat", sans-serif` (Google Fonts)
- Body: `"Inter", sans-serif` (Google Fonts)

**Font Sizes:**
- H1: 48px / 56px line-height (desktop), 32px / 40px (mobile)
- H2: 32px / 40px (desktop), 24px / 32px (mobile)
- H3: 24px / 32px (desktop), 20px / 28px (mobile)
- Body: 16px / 24px
- Small: 14px / 20px
- Caption: 12px / 16px

**Font Weights:**
- Regular: 400
- Medium: 500
- SemiBold: 600
- Bold: 700

### 2.4 Spacing System

**Base Unit:** 4px

**Spacing Scale:**
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px
- 4xl: 96px

**Section Padding:**
- Vertical: 64px (desktop), 48px (mobile)
- Horizontal: 24px (mobile), 48px (desktop)

### 2.5 Components

**Buttons:**

| Variant | Background | Text | Border | Hover |
|---------|------------|------|--------|-------|
| Primary | `#0059A8` | `#FFFFFF` | none | `#003D73` |
| Secondary | transparent | `#0059A8` | `2px #0059A8` | `#E8F1FA` bg |
| Disabled | `#D1D9E6` | `#9CA3AF` | none | - |

**Button Properties:**
- Border Radius: 8px
- Padding: 16px 32px
- Font: 16px, SemiBold (600)
- Transition: all 0.2s ease

**Form Inputs:**

| State | Background | Border | Text |
|-------|------------|--------|------|
| Default | `#FFFFFF` | `1px #D1D9E6` | `#1A1A2E` |
| Focus | `#FFFFFF` | `2px #0059A8` | `#1A1A2E` |
| Error | `#FEF2F2` | `2px #EF4444` | `#1A1A2E` |
| Disabled | `#F5F7FA` | `1px #E5E9F0` | `#9CA3AF` |

**Input Properties:**
- Border Radius: 8px
- Padding: 14px 16px
- Font: 16px, Regular (400)
- Height: 48px

**Checkboxes:**

- Size: 20px x 20px
- Border Radius: 4px
- Checked: Background `#0059A8`, checkmark white
- Unchecked: Background `#FFFFFF`, border `#D1D9E6`
- Label gap: 12px

**Cards:**
- Background: `#FFFFFF`
- Border Radius: 16px
- Shadow: `0 4px 6px -1px rgba(0, 37, 83, 0.1)`
- Padding: 32px

### 2.6 Visual Effects

**Shadows:**
- Card: `0 4px 6px -1px rgba(0, 37, 83, 0.1), 0 2px 4px -1px rgba(0, 37, 83, 0.06)`
- Button hover: `0 10px 15px -3px rgba(0, 37, 83, 0.1)`
- Input focus: `0 0 0 3px rgba(0, 89, 168, 0.1)`

**Animations:**
- Button hover: transform scale(1.02), box-shadow transition 0.2s
- Input focus: border-color 0.2s, box-shadow 0.2s
- Form submit: button loading state with spinner
- Page load: fade-in animation 0.5s

**Background:**
- Hero section: gradient linear from `#0059A8` to `#003D73`
- Subtle pattern overlay on hero (opacity 0.05)

---

## 3. Functionality Specification

### 3.1 Core Features

**1. Hero Section**
- Título principal attractivo: "Consigue cita para el padrón de Leganés"
- Subtítulo explicativo: "Te avisamos automáticamente cuando haya citas disponibles"
- Llamada a acción secundaria que desplaza al formulario

**2. How It Works Section**
- 3 pasos explicativos con iconos:
  1. "Regístrate" - Ingresa tus datos de contacto
  2. "Nosotros vigilamos" - Monitorizamos la web del ayuntamiento 24/7
  3. "Recibe alertas" - Te notificamos por tu canal preferido

**3. Registration Form**
- Campos requeridos:
  - Nombre completo (text, required)
  - Email (email, required, validation)
  - Teléfono (tel, required, for WhatsApp - format: +34XXXXXXXXX)
  - Telegram Chat ID (text, optional - with button to get it)
- Checkboxes para canales de notificación:
  - Email notifications (required, at least one)
  - Telegram notifications
  - WhatsApp notifications
- Botón de envío: "Registrarme" / "Activar alertas"
- Validación client-side de todos los campos

**4. Get Telegram Chat ID Button**
- Opens a modal or redirects to Telegram bot instructions
- Text: "¿No sabes tu Chat ID?" with link/bot to obtain it

**5. Success/Error States**
- Success: Mensaje de confirmación + instrucciones
- Error: Mensaje de error claro con sugerencia de solución

### 3.2 User Interactions

**Form Submission Flow:**
1. User fills all required fields
2. User selects at least one notification channel
3. User clicks "Registrarme"
4. Validation runs client-side
5. If valid → POST to backend API → Show success message
6. If invalid → Show inline error messages

**Telegram Chat ID Helper:**
- Click opens explanation modal/page
- Provides link to @userinfobot or custom bot
- Shows step-by-step instructions

### 3.3 Data Handling

**Form Data:**
```json
{
  "name": "string (required, min 2 chars)",
  "email": "string (required, valid email)",
  "phone": "string (required, format: +34XXXXXXXXX)",
  "telegram_chat_id": "string (optional)",
  "notification_channels": {
    "email": boolean (required, at least one true)",
    "telegram": boolean,
    "whatsapp": boolean
  }
}
```

**API Endpoint:**
- POST `/api/register`
- Response: 200 OK with confirmation or 400/500 with error

### 3.4 Edge Cases

- Email ya registrado → Mostrar mensaje de "ya registrado, ¿quieres actualizar?"
- Teléfono inválido → Validación de formato español
- Sin canales de notificación seleccionados → Mostrar error
- Fallo de conexión → Mostrar mensaje de error genérico con retry
- Usuario sin Telegram Chat ID pero quiere Telegram → Instrucciones claras

---

## 4. Acceptance Criteria

### 4.1 Visual Checkpoints

- [ ] El color azul `#0059A8` es dominante en botones primarios y acentos
- [ ] El fondo de la sección hero usa gradiente azul corporativo
- [ ] La tipografía Montserrat se usa en todos los encabezados
- [ ] La tipografía Inter se usa en el cuerpo de texto
- [ ] Todos los inputs tienen border-radius de 8px
- [ ] Los botones primarios tienen hover con cambio a `#003D73`
- [ ] El diseño es responsive y se adapta a móvil (320px+)
- [ ] El contraste de color cumple WCAG AA (4.5:1 mínimo)

### 4.2 Functional Checkpoints

- [ ] El formulario valida que el email tenga formato correcto
- [ ] El formulario valida que el teléfono tenga formato español (+34)
- [ ] Al menos un canal de notificación debe estar seleccionado
- [ ] El botón de Telegram Chat ID muestra instrucciones al hacer click
- [ ] El formulario muestra mensajes de error inline
- [ ] El botón de envío muestra estado de "cargando" al submitir
- [ ] El formulario muestra mensaje de éxito después del registro
- [ ] Todos los labels tienen asociados sus inputs (accesibilidad)

### 4.3 Accessibility Checkpoints

- [ ] Todos los inputs tienen labels visibles
- [ ] Los errores están asociados a los inputs con aria-describedby
- [ ] El contraste de texto cumple 4.5:1 mínimo
- [ ] Los botones tienen estados de focus visibles
- [ ] El formulario es navegable con teclado
- [ ] Los checkboxes tienen texto descriptivo

### 4.4 Performance Checkpoints

- [ ] Las fuentes se cargan desde Google Fonts
- [ ] No hay JavaScript innecesario en el initial load
- [ ] Las animaciones no superan 300ms
- [ ] La página carga en menos de 3 segundos en 3G

---

## 5. Assets Needed

**Icons (SVG inline):**
- Check icon (checkmark)
- Telegram icon
- WhatsApp icon
- Email/Mail icon
- Clock/Watch icon (vigilando)
- Bell icon (notificaciones)
- User/Person icon
- Phone icon
- Arrow/CTA icon

**External Resources:**
- Google Fonts: Montserrat (400, 500, 600, 700)
- Google Fonts: Inter (400, 500, 600)

---

## 6. File Structure

```
/workspace/pedircitapadronleganes/
├── SPEC.md                 # This specification
├── index.html              # Landing page HTML
├── styles/
│   └── main.css           # All styles
└── scripts/
    └── main.js            # Form validation and interactions
```
