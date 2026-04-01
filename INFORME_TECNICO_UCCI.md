# INFORME TÉCNICO
## Desarrollo Ágil de Aplicación con Inteligencia Artificial Generativa

**Proyecto:** Gestor de tareas con IA para estudiantes universitarios  
**Curso:** [Completar]  
**Docente:** [Completar]  
**Equipo:** [Completar integrantes]  
**Líder del equipo:** [Completar]  
**Fecha:** 30/03/2026

---

## 1. Introducción

El presente informe técnico describe el desarrollo de una aplicación sencilla orientada a estudiantes universitarios, cuyo objetivo es apoyar la organización académica mediante la gestión de tareas y el uso de inteligencia artificial generativa para sugerir planes de trabajo.  

Para esta primera entrega, el proyecto se presenta principalmente como un **prototipo funcional centrado en la experiencia de usuario y el frontend**, priorizando la interacción con tareas, horarios y planificación asistida por IA. Aunque la implementación técnica contempla componentes adicionales, el alcance documentado en este informe se enfoca en la funcionalidad observable por el usuario final.

---

## 2. Descripción del problema

Uno de los problemas más frecuentes en estudiantes universitarios es la dificultad para organizar sus actividades académicas y personales. En muchos casos, el estudiante debe gestionar cursos, trabajos, exposiciones, horarios de clase, evaluaciones y actividades extracurriculares al mismo tiempo. Esta carga genera:

- Falta de priorización de tareas.
- Olvido de fechas importantes.
- Dificultad para visualizar tiempos disponibles.
- Desorganización entre actividades académicas y personales.
- Baja productividad por ausencia de planificación concreta.

En este contexto, se identificó la necesidad de una solución simple, accesible y práctica que permitiera al estudiante registrar sus pendientes y recibir apoyo para organizar mejor su tiempo.

---

## 3. Solución propuesta

La solución propuesta consiste en una aplicación web de gestión de tareas con apoyo de inteligencia artificial, diseñada específicamente para estudiantes universitarios. La aplicación permite:

- Registrar tareas académicas o personales.
- Asignar prioridad a cada tarea.
- Organizar tareas según estado o categoría.
- Definir un horario base del estudiante.
- Generar un plan de trabajo asistido por IA según los pendientes registrados.
- Obtener sugerencias sobre huecos disponibles para avanzar tareas.

La propuesta busca que el estudiante no solo anote sus actividades, sino que también reciba una orientación práctica para ejecutarlas, mejorando su administración del tiempo y reduciendo la sobrecarga mental.

---

## 4. Alcance de la primera entrega

Para esta primera fase del proyecto se trabajó con un enfoque de **prototipo funcional orientado al frontend**, tomando como base los siguientes alcances:

- Interfaz funcional para visualizar tareas.
- Formulario para registrar y editar tareas.
- Gestión visual de prioridades, estados y categorías.
- Módulo de planificación con inteligencia artificial.
- Apartado de horario para que el estudiante registre sus bloques fijos.
- Flujo de interacción enfocado en usabilidad, claridad y apoyo al estudiante.

En este informe, la solución se presenta conceptualmente como una aplicación enfocada en la capa visible para el usuario, es decir, la experiencia de uso y el comportamiento funcional principal.

---

## 5. Metodología ágil utilizada

Se decidió utilizar **Scrum** como metodología ágil de trabajo, debido a que permite organizar el desarrollo en iteraciones cortas, priorizar funcionalidades y validar avances parciales con rapidez.

### 5.1 Justificación del uso de Scrum

Scrum fue elegido porque:

- Facilita dividir el trabajo en entregables pequeños y funcionales.
- Permite adaptar el desarrollo conforme aparecen nuevas necesidades.
- Favorece la colaboración del equipo.
- Ayuda a mantener visibilidad del avance del proyecto.
- Es apropiado para proyectos académicos con tiempo limitado.

### 5.2 Organización del equipo

Para cumplir con la actividad, el equipo se organiza bajo los siguientes roles:

- **Líder del equipo:** responsable de coordinar tareas, revisar avances y consolidar la entrega.
- **Desarrolladores:** responsables de la implementación de la interfaz, lógica funcional y documentación.
- **Apoyo técnico/documentación:** encargado de consolidar evidencias, justificar decisiones y apoyar en pruebas.

### 5.3 Product Backlog inicial

Se definieron como historias o necesidades principales:

1. Como estudiante, quiero registrar tareas para no olvidar mis pendientes.
2. Como estudiante, quiero asignar prioridad a mis tareas para saber qué hacer primero.
3. Como estudiante, quiero visualizar mi lista de tareas de forma clara.
4. Como estudiante, quiero registrar mi horario semanal para identificar tiempos disponibles.
5. Como estudiante, quiero que la IA me sugiera un plan de trabajo según mis tareas.
6. Como estudiante, quiero recibir una orientación práctica para aprovechar mis huecos libres.

### 5.4 Iteración Scrum aplicada

Se trabajó al menos una iteración ágil, estructurada de la siguiente manera:

**Sprint 1: Prototipo funcional del gestor de tareas con IA**

**Objetivo del sprint:**  
Construir una primera versión usable de la aplicación que permita al estudiante gestionar tareas y recibir apoyo de IA para organizarse.

**Duración estimada:**  
1 semana académica.

**Actividades del sprint:**

- Definición del problema y alcance.
- Diseño de la estructura general de la aplicación.
- Implementación de la vista principal de tareas.
- Implementación del formulario de registro y edición.
- Construcción del módulo de planificación con IA.
- Incorporación del apartado de horario del estudiante.
- Revisión de manejo de errores y mensajes de retroalimentación.
- Redacción del informe técnico.

**Entregables del sprint:**

- Aplicación funcional base.
- Interfaz de tareas operativa.
- Integración inicial con IA generativa.
- Flujo de planificación visible para el usuario.
- Informe técnico de la primera entrega.

### 5.5 Eventos Scrum considerados

Aunque el proyecto es académico y de alcance reducido, se aplicaron de manera simplificada los eventos principales de Scrum:

- **Sprint Planning:** definición del problema, alcance y tareas principales.
- **Daily Scrum informal:** seguimiento del avance del equipo y ajuste de pendientes.
- **Sprint Review:** revisión de la funcionalidad construida.
- **Sprint Retrospective:** identificación de mejoras, especialmente en usabilidad, claridad visual y flujo de interacción.

---

## 6. Uso de inteligencia artificial generativa

Uno de los requisitos de la actividad fue integrar herramientas de inteligencia artificial generativa en el desarrollo. En este proyecto se emplearon principalmente:

- **Claude**, para la generación y refinamiento del módulo de planificación asistida por IA.
- **Codex**, para apoyo en programación, revisión de estructura, mejoras de interfaz, redacción técnica y soporte de desarrollo.

### 6.1 Justificación del uso de IA

El uso de IA generativa se justificó porque permitió:

- Acelerar la construcción de componentes funcionales.
- Mejorar la redacción y estructura de ciertos bloques de código.
- Proponer mejoras de interfaz y experiencia de usuario.
- Apoyar la generación de prompts y lógica de planificación.
- Facilitar tareas de revisión, depuración y documentación técnica.

### 6.2 Forma en que se utilizó

La IA no se utilizó como sustituto del criterio del equipo, sino como herramienta de apoyo. Su uso se centró en:

- Sugerir estructuras iniciales de código.
- Refinar componentes visuales y formularios.
- Mejorar el flujo del módulo de planificación.
- Proponer manejo de errores más claro para el usuario.
- Ayudar a documentar decisiones técnicas del proyecto.

### 6.3 Impacto en el desarrollo

El impacto principal fue positivo, ya que permitió reducir tiempo en tareas repetitivas y concentrar el esfuerzo del equipo en adaptar la solución al problema planteado. Además, ayudó a mejorar la claridad del producto final y a incorporar funcionalidades más útiles para el usuario, como la planificación basada en tareas y horario.

---

## 7. Manejo de excepciones y robustez de la aplicación

Uno de los criterios principales de la actividad fue asegurar la robustez del software mediante manejo de excepciones. En la aplicación desarrollada se identifican diversas estrategias de control de errores y validación.

### 7.1 Validación de entradas del usuario

La aplicación valida información antes de procesarla. Algunos ejemplos son:

- Verificación de campos obligatorios.
- Validación de longitud mínima de contraseña.
- Confirmación de contraseña en el registro.
- Validación del título de las tareas.
- Restricción de prioridades válidas.
- Conversión segura de fechas.

Estas validaciones previenen comportamientos incorrectos antes de que el sistema continúe con la operación.

### 7.2 Manejo de errores en operaciones funcionales

La aplicación utiliza bloques `try/except` en los flujos principales para evitar que un error detenga por completo la experiencia del usuario. En lugar de interrumpir la ejecución, se muestran mensajes de retroalimentación claros.

Se manejan errores en acciones como:

- Registro de usuario.
- Inicio de sesión.
- Creación, edición y eliminación de tareas.
- Gestión de categorías.
- Guardado de horario.
- Generación del plan con IA.
- Continuación del chat con IA.
- Exportación de información.

### 7.3 Manejo de errores relacionados con IA

El módulo de inteligencia artificial incorpora tratamiento específico para distintos casos:

- Error de autenticación.
- Error de conexión.
- Límite de uso alcanzado.
- Error devuelto por la API.
- Error inesperado general.

Esto mejora la robustez del sistema, ya que evita fallos silenciosos y permite informar al usuario qué ocurrió.

### 7.4 Funciones auxiliares seguras

También se observan funciones auxiliares que retornan valores seguros en caso de error, por ejemplo:

- Retorno de listas vacías cuando no se puede cargar información.
- Validación de conversión de fechas.
- Generación controlada de contexto para la IA.

### 7.5 Aporte a la robustez

En conjunto, estas decisiones permiten que la aplicación:

- No se caiga ante errores comunes.
- Mantenga una experiencia comprensible para el usuario.
- Sea más estable frente a entradas inválidas o fallos externos.
- Cumpla con el criterio de manejo de excepciones solicitado en la actividad.

---

## 8. Aplicación de principios de código limpio

Durante el desarrollo se aplicaron diversos principios de código limpio orientados a mejorar mantenibilidad, claridad y reutilización.

### 8.1 Separación de responsabilidades

La solución se encuentra organizada por responsabilidades:

- Archivo principal para rutas y lógica de interacción.
- Modelos de datos definidos de forma separada.
- Capa de acceso a datos separada.
- Plantillas HTML organizadas por vistas.

Esta estructura favorece el mantenimiento y evita concentrar toda la lógica en un solo lugar.

### 8.2 Nombres descriptivos

Se emplean nombres claros para funciones, variables y rutas, por ejemplo:

- `generar_plan`
- `guardar_horario`
- `_parsear_fecha`
- `_construir_descripcion_tareas`
- `_obtener_cliente_ia`

Esto mejora la legibilidad y facilita comprender el propósito de cada bloque de código.

### 8.3 Modularidad y reutilización

Se identifican elementos reutilizables, como:

- Funciones auxiliares para validación y construcción de contexto.
- Plantillas reutilizables para formularios.
- Métodos de modelo para construir objetos desde datos.
- Componentes visuales compartidos entre vistas.

La reutilización reduce duplicidad y hace más fácil evolucionar el sistema.

### 8.4 Encapsulamiento de validaciones

Parte de la validación se centraliza en los modelos, por ejemplo en la validación de tareas. Esto permite que la lógica de consistencia no dependa únicamente de una vista o formulario específico.

### 8.5 Claridad estructural

El código presenta:

- Comentarios breves y útiles.
- Docstrings en varias funciones.
- Bloques seccionados por responsabilidades.
- Uso de tipos y parámetros opcionales en funciones.

Estas prácticas ayudan a que el código sea más entendible para otros desarrolladores.

---

## 9. Buenas prácticas de estilo de código

Además de los principios de código limpio, se aplicaron buenas prácticas de estilo que mejoran consistencia y legibilidad.

### 9.1 Consistencia en la organización

La aplicación mantiene una estructura coherente entre:

- rutas,
- validaciones,
- funciones auxiliares,
- plantillas,
- modelos.

### 9.2 Mensajes claros para el usuario

Se usan mensajes comprensibles para operaciones exitosas, advertencias y errores. Esto es importante no solo a nivel de experiencia de usuario, sino también como práctica de claridad funcional.

### 9.3 Tipado y legibilidad

El uso de anotaciones de tipo en varias funciones aporta una guía adicional sobre los datos que maneja el sistema.

### 9.4 Interfaz pensada para usabilidad

En la parte visual se consideraron prácticas que mejoran la experiencia:

- diseño claro y ordenado,
- separación entre tareas y horario,
- formulario de creación mediante diálogo,
- retroalimentación inmediata,
- visualización de prioridades y estados.

### 9.5 Programación defensiva

La validación previa de datos, el uso de valores por defecto y el control de excepciones son parte de un enfoque de programación defensiva que mejora la confiabilidad del sistema.

---

## 10. Refactorización aplicada

Durante el desarrollo se realizaron decisiones de refactorización para mejorar el producto sin alterar su propósito funcional.

### 10.1 Reorganización de componentes

Se separaron mejor las responsabilidades entre lógica de aplicación, modelos, acceso a datos y vistas, lo que reduce acoplamiento.

### 10.2 Extracción de funciones auxiliares

Se refactorizaron tareas repetitivas en funciones específicas, como:

- obtención de categorías,
- parseo de fechas,
- construcción del contexto para IA,
- re-renderizado del inicio para mantener el diálogo abierto.

### 10.3 Reutilización de plantillas

Se extrajeron componentes reutilizables del formulario de tareas para evitar duplicación de código en las vistas.

### 10.4 Mejora del flujo de interfaz

Se ajustó el flujo para que la creación de tareas sea más cómoda mediante un diálogo, y se separó el apartado de horario del módulo de IA para lograr una experiencia más coherente.

### 10.5 Refactorización orientada a claridad

El objetivo principal de la refactorización no fue solo “hacer que funcione”, sino lograr un código más entendible, mantenible y alineado con buenas prácticas.

---

## 11. Resultado funcional del proyecto

Como resultado de esta primera iteración, se obtuvo una aplicación funcional que permite al estudiante:

- registrar y organizar sus tareas,
- visualizar prioridades y estados,
- administrar un horario base,
- generar sugerencias de planificación mediante IA,
- interactuar con una interfaz clara y orientada a productividad.

El producto cumple con el propósito académico de demostrar el uso de metodologías ágiles, inteligencia artificial generativa, manejo de excepciones, código limpio, buenas prácticas de estilo y refactorización.

---

## 12. Conclusiones

1. Se logró desarrollar una aplicación sencilla pero funcional orientada a resolver un problema real de organización en estudiantes universitarios.
2. El uso de Scrum permitió ordenar el trabajo en una iteración concreta con entregables funcionales.
3. La integración de IA generativa mediante Claude y Codex aportó velocidad, apoyo técnico y mejora en la construcción del producto.
4. El manejo de excepciones implementado contribuye a la robustez y estabilidad de la aplicación.
5. La organización del código evidencia aplicación de principios de código limpio, buenas prácticas de estilo y refactorización.
6. La solución desarrollada constituye una base sólida para futuras mejoras, como mayor personalización, análisis de carga académica y ampliación de funcionalidades.

---

## 13. Recomendaciones

- Continuar con nuevas iteraciones Scrum para ampliar la solución.
- Mejorar la personalización del horario por días y bloques.
- Incorporar métricas de productividad del estudiante.
- Profundizar la interacción con IA para sugerencias más específicas.
- Mantener la práctica de refactorización continua durante futuras mejoras.

---

## 14. Referencias

- Schwaber, K., & Sutherland, J. *The Scrum Guide*.
- Martin, R. C. *Clean Code: A Handbook of Agile Software Craftsmanship*.
- Documentación de herramientas de inteligencia artificial generativa utilizadas en programación.
- Material de apoyo sobre manejo de excepciones en aplicaciones web desarrolladas en Python.

