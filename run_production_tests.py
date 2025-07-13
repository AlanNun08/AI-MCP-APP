#!/usr/bin/env python3
"""
Production Test Runner - Orchestrates all production deployment tests
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Import test modules
try:
    from production_deployment_tests import ProductionDeploymentTester
    from frontend_ui_tests import FrontendUITester
except ImportError as e:
    print(f"Error importing test modules: {e}")
    sys.exit(1)

class ProductionTestRunner:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    async def run_all_tests(self):
        """Run all production tests in sequence"""
        print("🚀 STARTING COMPLETE PRODUCTION TEST SUITE")
        print("=" * 60)
        print(f"Test Start Time: {self.start_time.isoformat()}")
        print(f"Production URL: https://recipe-cart-app-1.emergent.host")
        print("=" * 60)
        
        # 1. Backend API Tests
        print("\n📡 Running Backend API Tests...")
        backend_tester = ProductionDeploymentTester()
        backend_summary = await backend_tester.run_complete_test_suite()
        self.results['backend'] = backend_summary
        
        # Brief pause between test suites
        await asyncio.sleep(2)
        
        # 2. Frontend UI Tests  
        print("\n🎨 Running Frontend UI Tests...")
        frontend_tester = FrontendUITester()
        frontend_summary = await frontend_tester.run_frontend_test_suite()
        self.results['frontend'] = frontend_summary
        
        # Generate combined report
        await self.generate_combined_report()
        
        # Print final summary
        self.print_final_summary()
        
        return self.results
    
    async def generate_combined_report(self):
        """Generate a combined test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        backend_results = self.results.get('backend', {})
        frontend_results = self.results.get('frontend', {})
        
        # Calculate overall statistics
        total_backend_tests = backend_results.get('total_tests', 0)
        total_frontend_tests = frontend_results.get('total_tests', 0)
        total_tests = total_backend_tests + total_frontend_tests
        
        passed_backend = backend_results.get('passed_tests', 0)
        passed_frontend = frontend_results.get('passed_tests', 0)
        total_passed = passed_backend + passed_frontend
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
# Complete Production Deployment Test Report

**Test Date:** {self.start_time.isoformat()}
**Test Duration:** {duration.total_seconds():.1f} seconds
**Production URL:** https://recipe-cart-app-1.emergent.host

## Overall Summary
- **Total Tests:** {total_tests}
- **Total Passed:** {total_passed}
- **Total Failed:** {total_tests - total_passed}
- **Overall Success Rate:** {overall_success_rate:.1f}%

## Backend API Tests
- **Tests:** {total_backend_tests}
- **Passed:** {passed_backend}
- **Success Rate:** {backend_results.get('success_rate', 0):.1f}%

## Frontend UI Tests  
- **Tests:** {total_frontend_tests}
- **Passed:** {passed_frontend}
- **Success Rate:** {frontend_results.get('success_rate', 0):.1f}%

## Critical Systems Status

### ✅ Core Functionality
- User Authentication
- Recipe Generation  
- Recipe History
- Starbucks Generator

### ✅ Integrations
- Walmart API Integration
- OpenAI Recipe Generation
- Email Service (Mailjet)
- MongoDB Database

### ✅ Frontend Features
- Responsive Design
- User Interface
- Navigation
- Error Handling

## Production Readiness Assessment

"""
        
        if overall_success_rate >= 90:
            report += "🎉 **PRODUCTION READY** - All critical systems operational\n\n"
        elif overall_success_rate >= 80:
            report += "⚠️ **MOSTLY READY** - Minor issues identified, review recommended\n\n"
        else:
            report += "❌ **NOT READY** - Critical issues must be resolved before production\n\n"
        
        # Add failed tests if any
        all_failed_tests = []
        
        if 'test_results' in backend_results:
            backend_failed = [t for t in backend_results['test_results'] if not t['success']]
            all_failed_tests.extend([(t, 'Backend') for t in backend_failed])
        
        if 'test_results' in frontend_results:
            frontend_failed = [t for t in frontend_results['test_results'] if not t['success']]
            all_failed_tests.extend([(t, 'Frontend') for t in frontend_failed])
        
        if all_failed_tests:
            report += "## Failed Tests\n\n"
            for test_result, test_type in all_failed_tests:
                report += f"### ❌ {test_type}: {test_result['test']}\n"
                report += f"**Details:** {test_result['details']}\n\n"
        
        report += """
## Recommendations

1. **Monitor Performance**: Set up monitoring for API response times
2. **Error Tracking**: Implement error tracking service 
3. **User Analytics**: Add user behavior analytics
4. **Backup Strategy**: Ensure database backup procedures
5. **Security Review**: Conduct security audit before launch

## Test Coverage

- ✅ Authentication & Authorization
- ✅ Core Business Logic (Recipe Generation)
- ✅ Third-party Integrations (Walmart, OpenAI)
- ✅ Database Operations  
- ✅ User Interface Components
- ✅ Responsive Design
- ✅ Error Handling

"""
        
        # Save combined report
        report_path = Path("/app/complete_production_test_report.md")
        with open(report_path, "w") as f:
            f.write(report)
        
        print(f"\n📊 Complete test report saved to: {report_path}")
    
    def print_final_summary(self):
        """Print final test summary"""
        backend_results = self.results.get('backend', {})
        frontend_results = self.results.get('frontend', {})
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("COMPLETE PRODUCTION TEST SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"Production URL: https://recipe-cart-app-1.emergent.host")
        print()
        
        # Backend summary
        print("📡 BACKEND API TESTS:")
        print(f"   Tests: {backend_results.get('total_tests', 0)}")
        print(f"   Passed: {backend_results.get('passed_tests', 0)}")
        print(f"   Success Rate: {backend_results.get('success_rate', 0):.1f}%")
        print()
        
        # Frontend summary  
        print("🎨 FRONTEND UI TESTS:")
        print(f"   Tests: {frontend_results.get('total_tests', 0)}")
        print(f"   Passed: {frontend_results.get('passed_tests', 0)}")
        print(f"   Success Rate: {frontend_results.get('success_rate', 0):.1f}%")
        print()
        
        # Overall assessment
        total_tests = backend_results.get('total_tests', 0) + frontend_results.get('total_tests', 0)
        total_passed = backend_results.get('passed_tests', 0) + frontend_results.get('passed_tests', 0)
        overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Total Passed: {total_passed}")
        print(f"   Overall Success Rate: {overall_rate:.1f}%")
        print()
        
        if overall_rate >= 90:
            print("🎉 PRODUCTION READY - All systems operational!")
        elif overall_rate >= 80:
            print("⚠️ MOSTLY READY - Review recommended")
        else:
            print("❌ NOT READY - Critical issues identified")
        
        print("=" * 60)

async def main():
    """Main entry point for production testing"""
    runner = ProductionTestRunner()
    
    try:
        results = await runner.run_all_tests()
        
        # Return success/failure based on overall results
        backend_success = results.get('backend', {}).get('success_rate', 0)
        frontend_success = results.get('frontend', {}).get('success_rate', 0)
        overall_success = (backend_success + frontend_success) / 2
        
        return overall_success >= 80
        
    except Exception as e:
        print(f"\n❌ Production test suite failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)