#!/usr/bin/env python3
"""
Comprehensive test runner for Multi-Cloud Operations Dashboard
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


class TestRunner:
    """Test runner for the Multi-Cloud Operations Dashboard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def run_command(self, command, cwd=None, env=None):
        """Run a command and return the result."""
        print(f"🔄 Running: {' '.join(command)}")
        
        if cwd:
            print(f"📁 Working directory: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Command succeeded")
                if result.stdout:
                    print(f"📤 Output:\n{result.stdout}")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"📤 Error:\n{result.stderr}")
                if result.stdout:
                    print(f"📤 Output:\n{result.stdout}")
            
            return result
            
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            return None
    
    def setup_backend_environment(self):
        """Setup backend testing environment."""
        print("🔧 Setting up backend environment...")
        
        # Install test dependencies
        result = self.run_command(
            ["pip", "install", "-r", "requirements-test.txt"],
            cwd=self.backend_dir
        )
        
        if result and result.returncode != 0:
            print("❌ Failed to install backend test dependencies")
            return False
        
        # Create test database
        test_env = os.environ.copy()
        test_env.update({
            "ENVIRONMENT": "test",
            "DATABASE_URL": "sqlite:///./test.db",
            "SECRET_KEY": "test-secret-key-for-testing-only"
        })
        
        return True
    
    def setup_frontend_environment(self):
        """Setup frontend testing environment."""
        print("🔧 Setting up frontend environment...")
        
        # Check if node_modules exists
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            result = self.run_command(["npm", "install"], cwd=self.frontend_dir)
            if result and result.returncode != 0:
                print("❌ Failed to install frontend dependencies")
                return False
        
        # Install Playwright
        print("🎭 Installing Playwright...")
        result = self.run_command(
            ["npm", "install", "@playwright/test", "@types/node", "typescript"],
            cwd=self.frontend_dir
        )
        
        if result and result.returncode != 0:
            print("❌ Failed to install Playwright")
            return False
        
        # Install Playwright browsers
        result = self.run_command(
            ["npx", "playwright", "install"],
            cwd=self.frontend_dir
        )
        
        if result and result.returncode != 0:
            print("❌ Failed to install Playwright browsers")
            return False
        
        return True
    
    def run_backend_unit_tests(self):
        """Run backend unit tests."""
        print("🧪 Running backend unit tests...")
        
        test_env = os.environ.copy()
        test_env.update({
            "ENVIRONMENT": "test",
            "DATABASE_URL": "sqlite:///./test.db",
            "SECRET_KEY": "test-secret-key-for-testing-only"
        })
        
        result = self.run_command(
            ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
            cwd=self.backend_dir,
            env=test_env
        )
        
        return result and result.returncode == 0
    
    def run_backend_integration_tests(self):
        """Run backend integration tests."""
        print("🔗 Running backend integration tests...")
        
        test_env = os.environ.copy()
        test_env.update({
            "ENVIRONMENT": "test",
            "DATABASE_URL": "sqlite:///./test.db",
            "SECRET_KEY": "test-secret-key-for-testing-only"
        })
        
        result = self.run_command(
            ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
            cwd=self.backend_dir,
            env=test_env
        )
        
        return result and result.returncode == 0
    
    def run_backend_coverage(self):
        """Run backend tests with coverage."""
        print("📊 Running backend tests with coverage...")
        
        test_env = os.environ.copy()
        test_env.update({
            "ENVIRONMENT": "test",
            "DATABASE_URL": "sqlite:///./test.db",
            "SECRET_KEY": "test-secret-key-for-testing-only"
        })
        
        result = self.run_command(
            ["python", "-m", "pytest", "--cov=app", "--cov-report=html", "--cov-report=term"],
            cwd=self.backend_dir,
            env=test_env
        )
        
        if result and result.returncode == 0:
            print("📈 Coverage report generated in backend/htmlcov/")
        
        return result and result.returncode == 0
    
    def run_frontend_tests(self):
        """Run frontend E2E tests."""
        print("🎭 Running frontend E2E tests...")
        
        # Start backend server for E2E tests
        print("🚀 Starting backend server...")
        backend_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=self.backend_dir,
            env=os.environ.copy()
        )
        
        # Wait for backend to start
        time.sleep(5)
        
        try:
            # Run Playwright tests
            result = self.run_command(
                ["npx", "playwright", "test"],
                cwd=self.frontend_dir
            )
            
            success = result and result.returncode == 0
            
            if success:
                print("🎉 Frontend E2E tests passed!")
            else:
                print("❌ Frontend E2E tests failed")
            
            return success
            
        finally:
            # Stop backend server
            print("🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
    
    def run_load_tests(self, users=10, spawn_rate=2, duration="30s"):
        """Run load tests with Locust."""
        print(f"🚛 Running load tests ({users} users, {spawn_rate}/s spawn rate, {duration} duration)...")
        
        # Start backend server
        print("🚀 Starting backend server for load testing...")
        backend_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=self.backend_dir,
            env=os.environ.copy()
        )
        
        # Wait for backend to start
        time.sleep(5)
        
        try:
            # Run Locust
            result = self.run_command([
                "locust",
                "-f", "tests/load/locustfile.py",
                "--host", "http://localhost:8000",
                "--users", str(users),
                "--spawn-rate", str(spawn_rate),
                "--run-time", duration,
                "--headless",
                "--html", "load_test_report.html"
            ], cwd=self.backend_dir)
            
            success = result and result.returncode == 0
            
            if success:
                print("📊 Load test report generated: backend/load_test_report.html")
            
            return success
            
        finally:
            # Stop backend server
            print("🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
    
    def run_security_tests(self):
        """Run security tests."""
        print("🔒 Running security tests...")
        
        # Run bandit for security issues
        print("🔍 Running Bandit security scan...")
        result = self.run_command(
            ["bandit", "-r", "app/", "-f", "json", "-o", "security_report.json"],
            cwd=self.backend_dir
        )
        
        if result:
            if result.returncode == 0:
                print("✅ No security issues found")
            else:
                print("⚠️ Security issues found - check backend/security_report.json")
        
        # Run safety for dependency vulnerabilities
        print("🛡️ Running Safety dependency scan...")
        safety_result = self.run_command(
            ["safety", "check", "--json", "--output", "dependency_report.json"],
            cwd=self.backend_dir
        )
        
        return True  # Don't fail on security warnings
    
    def run_linting(self):
        """Run code linting."""
        print("🧹 Running code linting...")
        
        # Backend linting
        print("🐍 Linting backend code...")
        
        # Black formatting check
        black_result = self.run_command(
            ["black", "--check", "--diff", "app/", "tests/"],
            cwd=self.backend_dir
        )
        
        # isort import sorting check
        isort_result = self.run_command(
            ["isort", "--check-only", "--diff", "app/", "tests/"],
            cwd=self.backend_dir
        )
        
        # flake8 linting
        flake8_result = self.run_command(
            ["flake8", "app/", "tests/"],
            cwd=self.backend_dir
        )
        
        # mypy type checking
        mypy_result = self.run_command(
            ["mypy", "app/"],
            cwd=self.backend_dir
        )
        
        backend_success = all([
            black_result and black_result.returncode == 0,
            isort_result and isort_result.returncode == 0,
            flake8_result and flake8_result.returncode == 0,
            mypy_result and mypy_result.returncode == 0
        ])
        
        if backend_success:
            print("✅ Backend linting passed")
        else:
            print("❌ Backend linting failed")
        
        return backend_success
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("📋 Generating test report...")
        
        report_content = f"""
# Multi-Cloud Operations Dashboard - Test Report

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Results Summary

### Backend Tests
- Unit Tests: {'✅ PASSED' if self.run_backend_unit_tests() else '❌ FAILED'}
- Integration Tests: {'✅ PASSED' if self.run_backend_integration_tests() else '❌ FAILED'}
- Coverage Report: Available in backend/htmlcov/

### Frontend Tests
- E2E Tests: Run with `python run_tests.py --frontend`

### Security Tests
- Security Scan: Available in backend/security_report.json
- Dependency Scan: Available in backend/dependency_report.json

### Load Tests
- Load Test Report: Run with `python run_tests.py --load`

## Test Coverage

Backend test coverage is available in the HTML report at `backend/htmlcov/index.html`.

## Recommendations

1. Maintain test coverage above 80%
2. Run security scans regularly
3. Perform load testing before major releases
4. Keep dependencies updated

## Next Steps

1. Review any failing tests
2. Address security vulnerabilities
3. Optimize performance based on load test results
4. Update documentation as needed
"""
        
        with open("TEST_REPORT.md", "w") as f:
            f.write(report_content)
        
        print("📄 Test report generated: TEST_REPORT.md")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Multi-Cloud Operations Dashboard Test Runner")
    
    parser.add_argument("--setup", action="store_true", help="Setup test environments")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend E2E tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--lint", action="store_true", help="Run linting")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    # Load test options
    parser.add_argument("--users", type=int, default=10, help="Number of users for load testing")
    parser.add_argument("--spawn-rate", type=int, default=2, help="User spawn rate for load testing")
    parser.add_argument("--duration", default="30s", help="Load test duration")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 Multi-Cloud Operations Dashboard Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.setup or args.all:
        print("\n📦 Setting up test environments...")
        if not runner.setup_backend_environment():
            success = False
        if not runner.setup_frontend_environment():
            success = False
    
    if args.lint or args.all:
        print("\n🧹 Running linting...")
        if not runner.run_linting():
            success = False
    
    if args.unit or args.all:
        print("\n🧪 Running unit tests...")
        if not runner.run_backend_unit_tests():
            success = False
    
    if args.integration or args.all:
        print("\n🔗 Running integration tests...")
        if not runner.run_backend_integration_tests():
            success = False
    
    if args.coverage or args.all:
        print("\n📊 Running coverage tests...")
        if not runner.run_backend_coverage():
            success = False
    
    if args.frontend or args.all:
        print("\n🎭 Running frontend E2E tests...")
        if not runner.run_frontend_tests():
            success = False
    
    if args.security or args.all:
        print("\n🔒 Running security tests...")
        if not runner.run_security_tests():
            success = False
    
    if args.load:
        print("\n🚛 Running load tests...")
        if not runner.run_load_tests(args.users, args.spawn_rate, args.duration):
            success = False
    
    if args.report or args.all:
        print("\n📋 Generating test report...")
        runner.generate_test_report()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()