# Diagrama completo de procesos - ERP Oxylive

## 1. Arquitectura general

```mermaid
flowchart LR
    U["Usuario"] --> UI["Frontend ERP"]
    UI --> ANG["Angular - migracion progresiva"]
    UI --> LEG["Pantallas actuales HTML/JS"]
    ANG --> API["API FastAPI"]
    LEG --> API
    API --> AUTH["Autenticacion y roles"]
    API --> ODS["Operaciones y ODS"]
    API --> CRM["Clientes e interacciones"]
    API --> INV["Inventario y Kardex"]
    API --> PER["Personal y cargos"]
    AUTH --> DB[("PostgreSQL / SQLite")]
    ODS --> DB
    CRM --> DB
    INV --> DB
    PER --> DB
```

## 2. Acceso y distribucion por cargos

```mermaid
flowchart TD
    A["Ingreso por /login"] --> B["Usuario y contrasena"]
    B --> C["POST /auth/login"]
    C --> D{"Credenciales validas y usuario activo?"}
    D -- "No" --> E["Mostrar error de acceso"]
    D -- "Si" --> F["Cargar uno o varios cargos"]

    F --> G{"Tiene cargo administrativo?"}
    G -- "Si" --> H["Panel administrativo"]
    G -- "No" --> I{"Tiene cargo tecnico?"}
    I -- "Si" --> J["Panel operativo"]
    I -- "No" --> K["Acceso denegado"]

    H --> HA["Gerente general"]
    H --> HB["Coordinador administrativo"]
    H --> HC["Coordinador comercial"]
    H --> HD["Contador"]
    H --> HE["Juridico"]

    J --> JA["Tecnico de estacionarios"]
    J --> JB["Tecnico de portatiles"]
    J --> JC["Tecnico de llena"]
    J --> JD["Tecnico de compresores"]
```

## 3. Ciclo completo de una ODS

```mermaid
flowchart TD
    A["Crear ODS"] --> B["Seleccionar cliente"]
    B --> C["Registrar servicio y equipo"]
    C --> D["Tipo, marca, modelo, horas y modalidad"]
    D --> E{"Es llenado o recarga de tamices?"}
    E -- "Si" --> F["Registrar tabla de tamices: marca, cantidad y unidad/par"]
    E -- "No" --> G["Continuar con datos del equipo"]
    F --> H["Asignar tecnico principal"]
    G --> H
    H --> I["Estado: PENDIENTE DIAGNOSTICO - 10%"]

    I --> J{"Tecnico principal diagnostica directamente?"}
    J -- "Si" --> K["Diagnostico integral de estacionario o portatil"]
    J -- "No, transmite" --> L["Crear sub-ODS con el mismo numero de ODS"]

    L --> M{"Tipo de diagnostico especializado"}
    M -- "Compresor" --> N["Asignar a tecnico de compresores"]
    M -- "Tamices" --> O["Asignar a tecnico de llena"]

    N --> P["Diagnostico especializado de compresor"]
    P --> P1["Anillos, empaques, bielas, camisas, tapas y soportes"]
    P1 --> P2["Registrar requerimiento final del componente"]

    O --> Q["Diagnostico especializado de tamices"]
    Q --> Q1["Llenado, columnas, tapas y o-rings"]
    Q1 --> Q2["Registrar requerimiento final del componente"]

    P2 --> R["Adjuntar diagnostico a ODS madre"]
    Q2 --> R
    R --> S["Sub-ODS: DIAGNOSTICO LIBERADO - 100%"]
    S --> T{"Todas las sub-ODS fueron liberadas?"}
    T -- "No" --> U["ODS madre espera al especialista"]
    U --> T
    T -- "Si" --> V["Habilitar diagnostico final del tecnico principal"]

    K --> W["Preparar diagnostico final"]
    V --> X["Consolidar diagnosticos especializados"]
    X --> W
    W --> Y["Enviar reporte final a coordinacion"]
    Y --> Z["Estado: ESPERANDO APROBACION - 30%"]

    Z --> AA["Gerente o coordinador administrativo revisa reporte"]
    AA --> AB["Autorizar inicio del mantenimiento"]
    AB --> AC["Estado: APROBADO - EN EJECUCION - 60%"]
    AC --> AD["Tecnico ejecuta mantenimiento"]
    AD --> AE["Seleccionar repuestos utilizados"]
    AE --> AF["Cerrar ODS"]
    AF --> AG["Descontar inventario y registrar Kardex"]
    AG --> AH["Estado: FINALIZADO - 100%"]
```

## 4. Consolidacion del diagnostico especializado

```mermaid
sequenceDiagram
    participant TP as Tecnico principal
    participant ERP as ERP Oxylive
    participant TE as Tecnico especialista
    participant CO as Coordinador

    TP->>ERP: Crea sub-ODS ligada a la ODS madre
    ERP->>TE: Asigna diagnostico de compresor o tamices
    ERP-->>TP: ODS madre queda esperando especialista
    TE->>ERP: Marca componentes y registra requerimiento final
    ERP->>ERP: Guarda diagnostico especializado
    ERP->>ERP: Sub-ODS liberada al 100%
    ERP-->>TP: Habilita diagnostico final cuando todas esten liberadas
    TP->>ERP: Completa y envia diagnostico final
    ERP->>ERP: Adjunta los diagnosticos especializados
    ERP->>CO: Entrega reporte consolidado para aprobacion
    CO->>ERP: Autoriza ejecucion del mantenimiento
    ERP-->>TP: Habilita ejecucion y cierre
```

## 5. Inventario y Kardex

```mermaid
flowchart TD
    A["Catalogo de repuestos"] --> B["Nombre, unidad y stock minimo"]
    B --> C["Entrada de inventario"]
    C --> D["Aumentar cantidad disponible"]

    D --> E{"Tipo de salida"}
    E -- "Cierre de ODS" --> F["Tecnico selecciona repuestos y cantidades"]
    F --> G["Descuento automatico"]
    G --> H["Movimiento ligado a ODS, cliente y componente"]

    E -- "Salida manual" --> I["Registrar cantidad y justificacion"]
    I --> J["Descuento manual controlado"]

    H --> K["Kardex"]
    J --> K
    K --> L{"Stock menor o igual al minimo?"}
    L -- "Si" --> M["Alerta CRITICO"]
    L -- "No" --> N["Estado OPTIMO"]
```

## 6. Clientes e interacciones

```mermaid
flowchart TD
    A["Crear cliente"] --> B["Razon social"]
    B --> C["Natural o juridico"]
    C --> D["NIT o identificacion"]
    D --> E["Correo y telefono"]
    E --> F["Cliente disponible para nuevas ODS"]

    F --> G["Registrar interacciones"]
    G --> H["ODS creada"]
    G --> I["Diagnostico"]
    G --> J["Aprobacion"]
    G --> K["Cierre de ODS"]
    G --> L["Interaccion comercial o manual"]

    H --> M["Resumen CRM"]
    I --> M
    J --> M
    K --> M
    L --> M
    M --> N["Filtros por cliente, tipo y frecuencia"]
    N --> O["Indicadores y graficos"]
```

## 7. Personal, cargos y permisos

```mermaid
flowchart TD
    A["Gerente general"] --> B["Gestion de equipo"]
    B --> C["Crear usuario"]
    B --> D["Modificar usuario"]
    B --> E["Activar o desactivar usuario"]
    B --> F["Asignar varios cargos"]

    F --> G["Cargos administrativos"]
    F --> H["Cargos tecnicos"]

    G --> G1["Gerente general"]
    G --> G2["Coordinador administrativo"]
    G --> G3["Coordinador comercial"]
    G --> G4["Contador"]
    G --> G5["Juridico"]

    H --> H1["Tecnico de estacionarios"]
    H --> H2["Tecnico de portatiles"]
    H --> H3["Tecnico de llena"]
    H --> H4["Tecnico de compresores"]

    A --> I["Unico cargo autorizado para eliminar ODS"]
    G2 --> J["Puede aprobar diagnosticos finales"]
    A --> J
```

## 8. Estados principales

```mermaid
stateDiagram-v2
    [*] --> PendienteDiagnostico: ODS creada - 10%
    PendienteDiagnostico --> EsperandoEspecialista: Se crean sub-ODS
    EsperandoEspecialista --> PendienteDiagnostico: Diagnosticos especializados liberados
    PendienteDiagnostico --> EsperandoAprobacion: Diagnostico final enviado - 30%
    EsperandoAprobacion --> EnEjecucion: Coordinacion autoriza - 60%
    EnEjecucion --> Finalizado: Trabajo e inventario cerrados - 100%
    Finalizado --> [*]

    state "Sub-ODS especializada" as SubODS {
        [*] --> SubPendiente: Asignada - 10%
        SubPendiente --> SubLiberada: Diagnostico adjuntado - 100%
        SubLiberada --> [*]
    }
```

