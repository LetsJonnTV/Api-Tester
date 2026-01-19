# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Nothin here

## [1.0.0] - 2026-01-19

### Added

- **HTTP Request Support**
  - Alle gängigen HTTP-Methoden: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
  - Query Parameters mit Enable/Disable Toggle
  - Custom Headers mit Vorlagen für Common Headers
  - Multiple Body-Typen: JSON, XML, Form-Data, URL-Encoded, GraphQL

- **Authentication**
  - Basic Auth (Username/Password)
  - Bearer Token
  - API Key (Header oder Query Parameter)

- **Response Handling**
  - Pretty/Raw/Preview Formatierung
  - Automatische JSON/XML-Formatierung
  - Response Headers anzeigen
  - Cookies anzeigen
  - Suche in Response
  - Copy & Save Response

- **Automatic Tests**
  - Status Code Validierung
  - Response Time Check
  - Content-Type Validierung
  - JSON Validity Check

- **Organization**
  - Request History mit Suche
  - Collections mit Ordner-Struktur
  - Postman Collection Import

- **Environment Variables**
  - Variable Manager
  - `{{variable}}` Syntax in URLs, Headers und Body

- **Built-in Tools**
  - JSON Formatter & Minifier
  - Base64 Encoder/Decoder
  - URL Encoder/Decoder

- **User Interface**
  - 10+ Themes (Dark & Light)
  - Keyboard Shortcuts (Ctrl+N, Ctrl+Enter, F5)
  - Modern Design mit ttkbootstrap

- **Data Persistence**
  - Auto-Save für Headers und Environment Variables
  - Import/Export von Requests

- **Collection Management**: Vollständige Unterstützung zum Speichern von Requests in Collections
  - Neue 💾 (Save) und 🗑️ (Delete) Buttons in der Collection-Toolbar
  - Context-Menü für Collections (Rechtsklick)
  - Requests können per Doppelklick geladen werden
  - Requests werden mit Method-Farben angezeigt (🟢 GET, 🟡 POST, 🟠 PUT, 🟣 PATCH, 🔴 DELETE)
- **Save to Collection Dialog**: Benutzerfreundlicher Dialog zum Speichern von Requests mit Namenseingabe
- **Rename Function**: Elemente in Collections können umbenannt werden
- **Load from Collection**: Lädt alle Request-Daten (URL, Method, Headers, Body, Auth, Parameters)
- **History to Collection**: Requests aus der History können direkt in Collections gespeichert werden

[Unreleased]: https://github.com/username/api-tester/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/username/api-tester/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/username/api-tester/releases/tag/v1.0.0
