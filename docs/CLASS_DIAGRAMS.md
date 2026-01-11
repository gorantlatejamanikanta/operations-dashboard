# Multi-Cloud Operations Dashboard - Class Diagrams

## Backend Class Structure

### Core Authentication Classes

```mermaid
classDiagram
    class AuthService {
        -jwks_uri: str
        -issuer: str
        -audience: str
        -_jwks_cache: dict
        -_jwks_cache_time: datetime
        +__init__()
        +get_jwks() dict
        +verify_token(token: str) dict
    }
    
    class Settings {
        +ENVIRONMENT: str
        +DATABASE_URL: str
        +SECRET_KEY: str
        +AZURE_CLIENT_ID: str
        +AZURE_TENANT_ID: str
        +AZURE_OPENAI_API_KEY: str
        +CORS_ORIGINS: list[str]
        +__init__(**kwargs)
        +validate_settings()
    }
    
    class SecurityHeadersMiddleware {
        +dispatch(request: Request, call_next) Response
    }
    
    class RateLimitMiddleware {
        -calls: int
        -period: int
        -clients: defaultdict
        +__init__(app, calls: int, period: int)
        +dispatch(request: Request, call_next) Response
    }
    
    AuthService --> Settings : uses
    SecurityHeadersMiddleware --> Settings : uses
    RateLimitMiddleware --> Settings : uses
```

### Data Models

```mermaid
classDiagram
    class BaseModel {
        <<abstract>>
        +id: int
        +created_at: datetime
        +updated_at: datetime
    }
    
    class Project {
        +id: int
        +project_name: str
        +project_type: str
        +member_firm: str
        +deployed_region: str
        +is_active: bool
        +description: str
        +engagement_manager: str
        +project_startdate: date
        +project_enddate: date
        +status: ProjectStatus
        +progress_percentage: int
        +budget_allocated: int
        +budget_spent: int
        +priority: ProjectPriority
        +health_status: ProjectHealthStatus
        +resource_groups: list[ResourceGroup]
        +monthly_costs: list[MonthlyCost]
        +aiq_consumptions: list[AIQConsumption]
    }
    
    class ResourceGroup {
        +id: int
        +resource_group_name: str
        +project_id: int
        +status: str
        +project: Project
        +cost_data: list[CostData]
        +monthly_costs: list[MonthlyCost]
    }
    
    class CostData {
        +key: str
        +period: date
        +month_year: str
        +resource_group_id: int
        +cost: decimal
        +resource_group: ResourceGroup
    }
    
    class MonthlyCost {
        +project_id: int
        +resource_group_id: int
        +month: date
        +cost: decimal
        +project: Project
        +resource_group: ResourceGroup
    }
    
    class AIQConsumption {
        +id: int
        +project_id: int
        +aiq_assumption_name: str
        +consumption_amount: decimal
        +consumption_day: date
        +project: Project
    }
    
    class CloudConnection {
        +id: int
        +provider: str
        +connection_name: str
        +credentials: dict
        +is_active: bool
        +created_at: datetime
        +updated_at: datetime
    }
    
    BaseModel <|-- Project
    BaseModel <|-- ResourceGroup
    BaseModel <|-- AIQConsumption
    BaseModel <|-- CloudConnection
    
    Project ||--o{ ResourceGroup : "has many"
    Project ||--o{ MonthlyCost : "has many"
    Project ||--o{ AIQConsumption : "has many"
    ResourceGroup ||--o{ CostData : "has many"
    ResourceGroup ||--o{ MonthlyCost : "has many"
```

### Pydantic Schemas

```mermaid
classDiagram
    class ProjectBase {
        +project_name: str
        +project_type: str
        +member_firm: str
        +deployed_region: str
        +is_active: bool
        +description: str
        +project_startdate: date
        +project_enddate: date
        +status: ProjectStatus
        +progress_percentage: int
        +budget_allocated: int
        +validate_end_date(v, values) date
        +validate_project_type(v) str
        +validate_region(v) str
    }
    
    class ProjectCreate {
        +Config: class
    }
    
    class ProjectUpdate {
        +project_name: Optional[str]
        +project_type: Optional[str]
        +description: Optional[str]
        +progress_percentage: Optional[int]
    }
    
    class ProjectStatusUpdate {
        +status: ProjectStatus
        +progress_percentage: Optional[int]
        +health_status: Optional[ProjectHealthStatus]
        +status_notes: Optional[str]
        +Config: class
    }
    
    class Project {
        +id: int
        +model_config: ConfigDict
        +Config: class
    }
    
    class ChatMessage {
        +message: str
        +conversation_id: Optional[str]
        +validate_message(cls, v) str
        +validate_conversation_id(cls, v) str
        +Config: class
    }
    
    class ChatResponse {
        +response: str
        +sql_query: Optional[str]
        +conversation_id: str
        +Config: class
    }
    
    ProjectBase <|-- ProjectCreate
    ProjectBase <|-- Project
    ProjectCreate <|-- ProjectUpdate
```

### Service Classes

```mermaid
classDiagram
    class ChatService {
        -conversations: dict
        -system_prompt: str
        -client: AzureOpenAI
        +__init__()
        +_get_system_prompt() str
        +_get_schema_info() str
        +chat(message: str, conversation_id: str, db: Session) tuple
        +_extract_sql_query(message: str) Optional[str]
        +execute_query(query: str, db: Session) list[dict]
        +_format_query_results(results: list[dict]) str
    }
    
    class AWSService {
        -access_key_id: str
        -secret_access_key: str
        -region: str
        -session: boto3.Session
        +__init__(credentials: dict)
        +test_connection() bool
        +get_costs(start_date: date, end_date: date) list[dict]
        +get_resources() list[dict]
        +_create_cost_explorer_client() CostExplorer
        +_create_ec2_client() EC2
    }
    
    class AzureService {
        -client_id: str
        -client_secret: str
        -tenant_id: str
        -subscription_id: str
        -credential: ClientSecretCredential
        +__init__(credentials: dict)
        +test_connection() bool
        +get_costs(start_date: date, end_date: date) list[dict]
        +get_resources() list[dict]
        +_create_cost_management_client() CostManagementClient
        +_create_resource_client() ResourceManagementClient
    }
    
    class GCPService {
        -project_id: str
        -credentials: dict
        -client: Client
        +__init__(credentials: dict)
        +test_connection() bool
        +get_costs(start_date: date, end_date: date) list[dict]
        +get_resources() list[dict]
        +_create_billing_client() CloudBillingClient
        +_create_resource_client() CloudResourceManagerClient
    }
    
    class CloudProviderFactory {
        +create_service(provider: str, credentials: dict) CloudService
        +get_supported_providers() list[str]
    }
    
    CloudProviderFactory --> AWSService : creates
    CloudProviderFactory --> AzureService : creates
    CloudProviderFactory --> GCPService : creates
```

### API Router Classes

```mermaid
classDiagram
    class ProjectsRouter {
        +router: APIRouter
        +get_projects(skip: int, limit: int, status: str, region: str, db: Session, current_user: dict) list[Project]
        +get_project(project_id: int, db: Session, current_user: dict) Project
        +create_project(project: ProjectCreate, db: Session, current_user: dict) Project
        +update_project(project_id: int, project: ProjectUpdate, db: Session, current_user: dict) Project
        +update_project_status(project_id: int, status_update: ProjectStatusUpdate, db: Session, current_user: dict) Project
        +delete_project(project_id: int, db: Session, current_user: dict) dict
    }
    
    class ChatRouter {
        +router: APIRouter
        +chat_endpoint(chat_message: ChatMessage, db: Session, current_user: dict) ChatResponse
    }
    
    class CostsRouter {
        +router: APIRouter
        +get_costs(project_id: Optional[int], resource_group_id: Optional[int], db: Session, current_user: dict) list[dict]
        +create_cost(cost_data: dict, db: Session, current_user: dict) dict
    }
    
    class CloudProvidersRouter {
        +router: APIRouter
        +get_cloud_providers(db: Session, current_user: dict) list[CloudConnection]
        +create_cloud_provider(connection_data: dict, db: Session, current_user: dict) CloudConnection
        +test_connection(test_data: dict, current_user: dict) dict
        +get_provider_costs(provider_id: int, request_data: dict, db: Session, current_user: dict) list[dict]
    }
    
    class DashboardRouter {
        +router: APIRouter
        +get_dashboard_summary(db: Session, current_user: dict) dict
        +get_project_metrics(db: Session, current_user: dict) dict
        +get_cost_metrics(db: Session, current_user: dict) dict
    }
    
    ProjectsRouter --> Project : uses
    ProjectsRouter --> ProjectCreate : uses
    ProjectsRouter --> ProjectUpdate : uses
    ChatRouter --> ChatMessage : uses
    ChatRouter --> ChatResponse : uses
    ChatRouter --> ChatService : uses
    CloudProvidersRouter --> CloudConnection : uses
    CloudProvidersRouter --> AWSService : uses
    CloudProvidersRouter --> AzureService : uses
```

## Frontend Class Structure

### React Component Hierarchy

```mermaid
classDiagram
    class App {
        +render() JSX.Element
    }
    
    class Layout {
        +children: ReactNode
        +render() JSX.Element
    }
    
    class Navigation {
        +currentPath: string
        +render() JSX.Element
    }
    
    class ThemeProvider {
        +children: ReactNode
        +theme: string
        +toggleTheme() void
        +render() JSX.Element
    }
    
    class Dashboard {
        +metrics: DashboardMetrics
        +loading: boolean
        +error: string
        +fetchDashboardData() Promise<void>
        +render() JSX.Element
    }
    
    class ProjectsPage {
        +projects: Project[]
        +viewMode: string
        +showForm: boolean
        +loading: boolean
        +fetchProjects() Promise<void>
        +handleCreateProject(data: ProjectCreate) Promise<void>
        +render() JSX.Element
    }
    
    class ProjectForm {
        +editProject: Project
        +onSuccess: () => void
        +formData: ProjectFormData
        +handleSubmit(data: ProjectCreate) Promise<void>
        +validateForm(data: ProjectFormData) ValidationResult
        +render() JSX.Element
    }
    
    class ProjectStatusManager {
        +projects: Project[]
        +searchTerm: string
        +statusFilter: string
        +regionFilter: string
        +onProjectUpdate: () => void
        +fetchProjects() Promise<void>
        +updateProjectStatus(id: number, status: boolean) Promise<void>
        +render() JSX.Element
    }
    
    class ProjectIntakeForm {
        +currentStep: number
        +formData: IntakeFormData
        +onSuccess: () => void
        +onCancel: () => void
        +nextStep() void
        +previousStep() void
        +handleSubmit() Promise<void>
        +render() JSX.Element
    }
    
    class ChatBot {
        +messages: ChatMessage[]
        +inputValue: string
        +conversationId: string
        +loading: boolean
        +sendMessage(message: string) Promise<void>
        +render() JSX.Element
    }
    
    App --> Layout : contains
    Layout --> Navigation : contains
    Layout --> ThemeProvider : contains
    App --> Dashboard : routes to
    App --> ProjectsPage : routes to
    ProjectsPage --> ProjectForm : contains
    ProjectsPage --> ProjectStatusManager : contains
    ProjectsPage --> ProjectIntakeForm : contains
    Dashboard --> ChatBot : contains
```

### Custom Hooks

```mermaid
classDiagram
    class useAuth {
        +user: User
        +loading: boolean
        +error: string
        +login() Promise<void>
        +logout() void
        +isAuthenticated() boolean
    }
    
    class useApi {
        +loading: boolean
        +error: string
        +data: any
        +get(url: string) Promise<any>
        +post(url: string, data: any) Promise<any>
        +put(url: string, data: any) Promise<any>
        +delete(url: string) Promise<any>
    }
    
    class useProjects {
        +projects: Project[]
        +loading: boolean
        +error: string
        +fetchProjects() Promise<void>
        +createProject(data: ProjectCreate) Promise<Project>
        +updateProject(id: number, data: ProjectUpdate) Promise<Project>
        +deleteProject(id: number) Promise<void>
    }
    
    class useChat {
        +messages: ChatMessage[]
        +loading: boolean
        +conversationId: string
        +sendMessage(message: string) Promise<void>
        +clearConversation() void
    }
    
    class useTheme {
        +theme: string
        +toggleTheme() void
        +setTheme(theme: string) void
    }
    
    useProjects --> useApi : uses
    useChat --> useApi : uses
    useAuth --> useApi : uses
```

### Context Providers

```mermaid
classDiagram
    class ThemeContext {
        +theme: string
        +setTheme: (theme: string) => void
        +toggleTheme: () => void
    }
    
    class AuthContext {
        +user: User
        +login: () => Promise<void>
        +logout: () => void
        +isAuthenticated: boolean
        +loading: boolean
    }
    
    class ApiContext {
        +baseURL: string
        +headers: Record<string, string>
        +request: (config: RequestConfig) => Promise<any>
    }
    
    class ThemeProvider {
        +children: ReactNode
        +value: ThemeContext
        +render() JSX.Element
    }
    
    class AuthProvider {
        +children: ReactNode
        +value: AuthContext
        +render() JSX.Element
    }
    
    class ApiProvider {
        +children: ReactNode
        +value: ApiContext
        +render() JSX.Element
    }
    
    ThemeProvider --> ThemeContext : provides
    AuthProvider --> AuthContext : provides
    ApiProvider --> ApiContext : provides
```

## Testing Class Structure

### Backend Test Classes

```mermaid
classDiagram
    class TestAuthService {
        +test_init() void
        +test_get_jwks_success() void
        +test_get_jwks_failure() void
        +test_verify_token_success() void
        +test_verify_token_missing_kid() void
        +test_verify_token_jwt_error() void
    }
    
    class TestChatService {
        +test_init_without_azure_openai() void
        +test_init_with_azure_openai() void
        +test_chat_without_openai_client() void
        +test_chat_with_openai_client() void
        +test_execute_query_valid_select() void
        +test_execute_query_invalid_statement() void
        +test_execute_query_dangerous_keyword() void
    }
    
    class TestProjectsAPI {
        +test_get_projects_empty() void
        +test_get_projects_with_data() void
        +test_create_project() void
        +test_update_project() void
        +test_delete_project() void
        +test_get_projects_pagination() void
        +test_get_projects_filtering() void
    }
    
    class TestChatAPI {
        +test_chat_without_openai() void
        +test_chat_with_openai_success() void
        +test_chat_input_validation() void
        +test_chat_sql_injection_protection() void
    }
    
    class MockAzureService {
        +authenticated: boolean
        +get_costs(start_date: date, end_date: date) list[dict]
        +get_resources() list[dict]
    }
    
    class MockAWSService {
        +authenticated: boolean
        +get_costs(start_date: date, end_date: date) list[dict]
        +get_resources() list[dict]
    }
    
    TestProjectsAPI --> MockAzureService : uses
    TestChatAPI --> MockAWSService : uses
```

### Frontend Test Classes (Playwright)

```mermaid
classDiagram
    class DashboardTests {
        +test_load_dashboard_page() void
        +test_display_key_metrics_cards() void
        +test_display_charts_and_visualizations() void
        +test_navigate_to_projects_page() void
        +test_toggle_theme() void
        +test_responsive_on_mobile() void
    }
    
    class ProjectsTests {
        +test_load_projects_page() void
        +test_create_new_project_via_quick_add() void
        +test_filter_projects_by_search() void
        +test_update_project_status() void
        +test_complete_full_intake_form() void
        +test_handle_empty_state() void
    }
    
    class ChatTests {
        +test_send_chat_message() void
        +test_display_sql_query() void
        +test_conversation_continuity() void
        +test_handle_api_errors() void
    }
    
    class BasePage {
        +page: Page
        +goto(url: string) Promise<void>
        +waitForLoadState() Promise<void>
        +screenshot() Promise<Buffer>
    }
    
    class ProjectsPage {
        +clickQuickAdd() Promise<void>
        +fillProjectForm(data: ProjectData) Promise<void>
        +submitForm() Promise<void>
        +searchProjects(term: string) Promise<void>
    }
    
    class DashboardPage {
        +getMetricsCards() Promise<Locator[]>
        +getCharts() Promise<Locator[]>
        +toggleTheme() Promise<void>
    }
    
    BasePage <|-- ProjectsPage
    BasePage <|-- DashboardPage
    DashboardTests --> DashboardPage : uses
    ProjectsTests --> ProjectsPage : uses
```

## Utility Classes

### Backend Utilities

```mermaid
classDiagram
    class DatabaseManager {
        +engine: Engine
        +SessionLocal: sessionmaker
        +create_tables() void
        +get_db() Generator[Session]
        +reset_database() void
    }
    
    class ConfigValidator {
        +validate_environment_variables() bool
        +validate_database_connection() bool
        +validate_azure_configuration() bool
        +validate_cors_origins() bool
    }
    
    class SecurityUtils {
        +generate_secret_key() str
        +hash_password(password: str) str
        +verify_password(password: str, hashed: str) bool
        +create_jwt_token(data: dict) str
        +verify_jwt_token(token: str) dict
    }
    
    class QueryValidator {
        +is_safe_query(query: str) bool
        +check_dangerous_keywords(query: str) bool
        +validate_query_length(query: str) bool
        +sanitize_query(query: str) str
    }
    
    DatabaseManager --> Settings : uses
    ConfigValidator --> Settings : uses
    SecurityUtils --> Settings : uses
    ChatService --> QueryValidator : uses
```

### Frontend Utilities

```mermaid
classDiagram
    class ApiClient {
        +baseURL: string
        +defaultHeaders: Record<string, string>
        +get(endpoint: string, config?: RequestConfig) Promise<any>
        +post(endpoint: string, data: any, config?: RequestConfig) Promise<any>
        +put(endpoint: string, data: any, config?: RequestConfig) Promise<any>
        +delete(endpoint: string, config?: RequestConfig) Promise<any>
        +setAuthToken(token: string) void
    }
    
    class FormValidator {
        +validateRequired(value: any) ValidationResult
        +validateEmail(email: string) ValidationResult
        +validateDate(date: string) ValidationResult
        +validateDateRange(startDate: string, endDate: string) ValidationResult
        +validateBudget(amount: number) ValidationResult
    }
    
    class DateUtils {
        +formatDate(date: Date, format: string) string
        +parseDate(dateString: string) Date
        +isValidDateRange(start: Date, end: Date) boolean
        +getDateRangeOptions() DateRangeOption[]
    }
    
    class ThemeUtils {
        +getSystemTheme() string
        +applyTheme(theme: string) void
        +toggleTheme(currentTheme: string) string
        +saveThemePreference(theme: string) void
        +loadThemePreference() string
    }
    
    class StorageUtils {
        +setItem(key: string, value: any) void
        +getItem(key: string) any
        +removeItem(key: string) void
        +clear() void
    }
    
    ApiClient --> StorageUtils : uses
    ThemeUtils --> StorageUtils : uses
```

This comprehensive class diagram documentation provides a detailed view of the object-oriented structure of the Multi-Cloud Operations Dashboard, covering both backend and frontend components, their relationships, and key methods.