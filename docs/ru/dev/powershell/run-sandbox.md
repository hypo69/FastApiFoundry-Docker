# run-sandbox.ps1 — Запуск Windows Sandbox

Скрипт автоматически проверяет окружение, включает необходимые компоненты Windows и запускает **Windows Sandbox** с примонтированной папкой проекта.

---

## Требования

| Требование | Минимум |
|---|---|
| Windows | 10 Pro / Enterprise / Education (build 18305+) или Windows 11 |
| PowerShell | 5.1+ |
| Права | Администратор |
| BIOS | Виртуализация включена (Intel VT-x / AMD-V) |

> 💡 **Проверить виртуализацию:** Диспетчер задач → вкладка **Производительность** → раздел **ЦП** → строка **Виртуализация: включено**

> ⚙️ **Включить Windows Sandbox:** `Win+R` → `appwiz.cpl` → **Включение или отключение компонентов Windows** → отметить **Windows Sandbox**

> 📖 **Подробная инструкция:** [remontka.pro/sandbox-windows/#enable](https://remontka.pro/sandbox-windows/#enable)

---

## Использование

```powershell
# Интерактивный режим — открывает PowerShell-консоль внутри sandbox
powershell -ExecutionPolicy Bypass -File .\run-sandbox.ps1

# Silent-режим — запускает autostart.ps1 в скрытом окне
powershell -ExecutionPolicy Bypass -File .\run-sandbox.ps1 -Silent
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `-Silent` | switch | `$false` | Запускает `autostart.ps1` в скрытом режиме вместо интерактивного `start.ps1` |

---

## Логика работы

```
run-sandbox.ps1
    │
    ├─ Test-Virtualization()
    │       systeminfo → проверка "Virtualization Enabled In Firmware: Yes"
    │       └─ если нет → throw (завершение)
    │
    ├─ Ensure-Sandbox()
    │       ├─ Enable-Feature("Microsoft-Hyper-V")
    │       ├─ Enable-Feature("VirtualMachinePlatform")
    │       ├─ Enable-Feature("Containers-DisposableClientVM")
    │       ├─ bcdedit /set hypervisorlaunchtype Auto
    │       └─ возвращает $rebootRequired
    │
    ├─ если $rebootRequired → Restart-Computer
    │
    ├─ New-WSBConfig(-silent)
    │       └─ генерирует %TEMP%\sandbox_auto.wsb
    │
    └─ Start-Sandbox()
            └─ Start-Process sandbox_auto.wsb
```

---

## Функции

### `Test-Virtualization`

Проверяет вывод `systeminfo` на наличие строки `Virtualization Enabled In Firmware: Yes`.

**Возвращает:** `bool`

---

### `Enable-Feature`

Включает опциональный компонент Windows через `Enable-WindowsOptionalFeature`.

| Параметр | Тип | Описание |
|---|---|---|
| `$name` | string | Имя компонента (`Microsoft-Hyper-V`, `VirtualMachinePlatform`, `Containers-DisposableClientVM`) |

**Возвращает:** `bool` — `$true` если компонент был только что включён (требуется перезагрузка)

---

### `Ensure-Sandbox`

Оркестрирует проверку виртуализации и включение всех трёх компонентов. Устанавливает `hypervisorlaunchtype Auto` через `bcdedit`.

**Возвращает:** `bool` — `$true` если нужна перезагрузка

**Исключение:** бросает строку `'Виртуализация отключена в BIOS'` если виртуализация недоступна

---

### `New-WSBConfig`

Генерирует XML-файл `.wsb` в `%TEMP%\sandbox_auto.wsb`.

| Параметр | Тип | Описание |
|---|---|---|
| `$silent` | bool | Режим запуска внутри sandbox |

**Режимы LogonCommand:**

```
Silent = $false  →  powershell.exe -NoExit -ExecutionPolicy Bypass -Command "cd '...'; ./start.ps1"
Silent = $true   →  powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "cd '...'; ./autostart.ps1"
```

**Маппинг папок:**

| Хост | Sandbox |
|---|---|
| `D:\repos\public_repositories\FastApiFoundry-Docker` | `C:\Users\WDAGUtilityAccount\Desktop\FastApiFoundry-Docker` |

---

### `Start-Sandbox`

Запускает `sandbox_auto.wsb` через `Start-Process`. Windows сам открывает файл в `WindowsSandbox.exe`.

---

## Переменные конфигурации

Заданы в начале скрипта — при необходимости изменить пути:

```powershell
$PROJECT_PATH = 'D:\repos\public_repositories\FastApiFoundry-Docker'
$SANDBOX_PATH = 'C:\Users\WDAGUtilityAccount\Desktop\FastApiFoundry-Docker'
$WSB_FILE     = Join-Path $env:TEMP 'sandbox_auto.wsb'
```

---

## Устранение неполадок

| Симптом | Причина | Решение |
|---|---|---|
| `Виртуализация отключена в BIOS` | VT-x / AMD-V выключен | Проверить: Диспетчер задач → Производительность → ЦП → «Виртуализация». Включить в BIOS/UEFI если отключена |
| Sandbox не появляется в списке компонентов | Windows Home edition | Нужна Pro / Enterprise / Education |
| Скрипт завершается без ошибок, но sandbox не открывается | `.wsb` не ассоциирован | Установить Windows Sandbox через «Компоненты Windows» |
| После включения компонентов требуется перезагрузка | Нормальное поведение | Перезапустить ПК, затем повторить скрипт |

> 📖 Подробная инструкция по установке и включению Sandbox:  
> **[https://remontka.pro/sandbox-windows/#enable](https://remontka.pro/sandbox-windows/#enable)**
