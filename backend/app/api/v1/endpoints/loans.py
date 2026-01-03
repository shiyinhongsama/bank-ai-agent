"""
贷款API端点
"""

import logging
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime

from app.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# 模拟贷款产品数据
mock_loan_products = [
    {
        "id": 1,
        "name": "个人消费贷款",
        "product_code": "LOAN001",
        "loan_type": "consumer",
        "min_amount": 10000,
        "max_amount": 500000,
        "min_term_months": 6,
        "max_term_months": 36,
        "interest_rate": 4.35,
        "processing_fee": 0.0,
        "early_repayment_fee": 0.0,
        "min_income": 3000,
        "min_credit_score": 600,
        "max_debt_to_income": 0.5,
        "is_available": True,
        "description": "用于个人消费的信用贷款产品",
        "requirements": "年满18周岁，有稳定收入来源",
        "terms_conditions": "提前还款无手续费，需提前7天申请"
    },
    {
        "id": 2,
        "name": "房贷",
        "product_code": "LOAN002",
        "loan_type": "mortgage",
        "min_amount": 100000,
        "max_amount": 10000000,
        "min_term_months": 60,
        "max_term_months": 360,
        "interest_rate": 3.85,
        "processing_fee": 0.0,
        "early_repayment_fee": 0.0,
        "min_income": 8000,
        "min_credit_score": 650,
        "max_debt_to_income": 0.4,
        "is_available": True,
        "description": "用于购买住房的贷款产品",
        "requirements": "首套房，需提供收入证明和购房合同",
        "terms_conditions": "LPR+基点定价，提前还款可能收取违约金"
    }
]

# 模拟贷款申请数据
mock_loan_applications = [
    {
        "id": 1,
        "user_id": 1,
        "product_id": 1,
        "application_number": "APP20241201001",
        "requested_amount": 100000,
        "requested_term_months": 24,
        "purpose": "装修",
        "monthly_income": 8000,
        "employment_status": "在职",
        "employer_name": "某科技有限公司",
        "work_years": 3,
        "status": "approved",
        "submitted_at": "2024-11-15T10:30:00",
        "reviewed_at": "2024-11-16T14:20:00",
        "approved_amount": 100000,
        "approved_term_months": 24,
        "approved_interest_rate": 4.35,
        "reviewer_notes": "申请材料完整，收入稳定，批准放款",
        "rejection_reason": None
    }
]

class LoanProductResponse(BaseModel):
    """贷款产品响应模型"""
    id: int
    name: str
    product_code: str
    loan_type: str
    min_amount: float
    max_amount: float
    min_term_months: int
    max_term_months: int
    interest_rate: float
    processing_fee: float
    min_income: float
    min_credit_score: int
    is_available: bool
    description: str
    requirements: str

class LoanApplicationRequest(BaseModel):
    """贷款申请请求模型"""
    product_id: int
    requested_amount: float
    requested_term_months: int
    purpose: str
    monthly_income: float
    employment_status: str
    employer_name: str = None
    work_years: int = None

class LoanApplicationResponse(BaseModel):
    """贷款申请响应模型"""
    id: int
    application_number: str
    product_name: str
    requested_amount: float
    requested_term_months: int
    status: str
    submitted_at: datetime
    approved_amount: float = None
    approved_interest_rate: float = None

@router.get("/products", response_model=List[LoanProductResponse])
async def get_loan_products(
    loan_type: str = None,
    max_amount: float = None,
    db = Depends(get_db)
):
    """获取贷款产品列表"""
    try:
        products = mock_loan_products.copy()
        
        # 按贷款类型筛选
        if loan_type:
            products = [p for p in products if p["loan_type"] == loan_type]
        
        # 按最高金额筛选
        if max_amount:
            products = [p for p in products if p["min_amount"] <= max_amount]
        
        # 只返回可用的产品
        products = [p for p in products if p["is_available"]]
        
        logger.info(f"📊 获取贷款产品列表: {len(products)} 个产品")
        
        return [
            LoanProductResponse(
                id=product["id"],
                name=product["name"],
                product_code=product["product_code"],
                loan_type=product["loan_type"],
                min_amount=product["min_amount"],
                max_amount=product["max_amount"],
                min_term_months=product["min_term_months"],
                max_term_months=product["max_term_months"],
                interest_rate=product["interest_rate"],
                processing_fee=product["processing_fee"],
                min_income=product["min_income"],
                min_credit_score=product["min_credit_score"],
                is_available=product["is_available"],
                description=product["description"],
                requirements=product["requirements"]
            )
            for product in products
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取贷款产品列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取贷款产品列表失败")

@router.get("/products/{product_id}", response_model=LoanProductResponse)
async def get_loan_product(product_id: int, db = Depends(get_db)):
    """获取特定贷款产品详情"""
    try:
        product = next((p for p in mock_loan_products if p["id"] == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="贷款产品不存在")
        
        logger.info(f"📊 获取贷款产品详情: {product_id}")
        
        return LoanProductResponse(
            id=product["id"],
            name=product["name"],
            product_code=product["product_code"],
            loan_type=product["loan_type"],
            min_amount=product["min_amount"],
            max_amount=product["max_amount"],
            min_term_months=product["min_term_months"],
            max_term_months=product["max_term_months"],
            interest_rate=product["interest_rate"],
            processing_fee=product["processing_fee"],
            min_income=product["min_income"],
            min_credit_score=product["min_credit_score"],
            is_available=product["is_available"],
            description=product["description"],
            requirements=product["requirements"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取贷款产品详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取贷款产品详情失败")

@router.post("/applications", response_model=LoanApplicationResponse)
async def create_loan_application(
    application: LoanApplicationRequest,
    user_id: int = 1,
    db = Depends(get_db)
):
    """创建贷款申请"""
    try:
        # 验证产品是否存在
        product = next((p for p in mock_loan_products if p["id"] == application.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="贷款产品不存在")
        
        # 验证申请条件
        if application.requested_amount < product["min_amount"]:
            raise HTTPException(status_code=400, detail=f"申请金额不能低于 {product['min_amount']} 元")
        
        if application.requested_amount > product["max_amount"]:
            raise HTTPException(status_code=400, detail=f"申请金额不能超过 {product['max_amount']} 元")
        
        if application.requested_term_months < product["min_term_months"]:
            raise HTTPException(status_code=400, detail=f"申请期限不能低于 {product['min_term_months']} 个月")
        
        if application.requested_term_months > product["max_term_months"]:
            raise HTTPException(status_code=400, detail=f"申请期限不能超过 {product['max_term_months']} 个月")
        
        # 生成申请编号
        application_number = f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id:03d}"
        
        # 创建申请记录（在实际项目中应该保存到数据库）
        application_id = len(mock_loan_applications) + 1
        
        logger.info(f"✅ 贷款申请创建成功: {application_number}")
        
        return LoanApplicationResponse(
            id=application_id,
            application_number=application_number,
            product_name=product["name"],
            requested_amount=application.requested_amount,
            requested_term_months=application.requested_term_months,
            status="submitted",
            submitted_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建贷款申请失败: {e}")
        raise HTTPException(status_code=500, detail="创建贷款申请失败")

@router.get("/applications", response_model=List[LoanApplicationResponse])
async def get_loan_applications(user_id: int = 1, db = Depends(get_db)):
    """获取用户贷款申请列表"""
    try:
        # 筛选用户申请
        applications = [
            app for app in mock_loan_applications 
            if app["user_id"] == user_id
        ]
        
        # 获取产品名称
        product_map = {p["id"]: p["name"] for p in mock_loan_products}
        
        logger.info(f"📊 获取贷款申请列表: 用户 {user_id}, {len(applications)} 个申请")
        
        return [
            LoanApplicationResponse(
                id=app["id"],
                application_number=app["application_number"],
                product_name=product_map.get(app["product_id"], "未知产品"),
                requested_amount=app["requested_amount"],
                requested_term_months=app["requested_term_months"],
                status=app["status"],
                submitted_at=datetime.fromisoformat(app["submitted_at"]),
                approved_amount=app.get("approved_amount"),
                approved_interest_rate=app.get("approved_interest_rate")
            )
            for app in applications
        ]
        
    except Exception as e:
        logger.error(f"❌ 获取贷款申请列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取贷款申请列表失败")

@router.get("/applications/{application_id}", response_model=LoanApplicationResponse)
async def get_loan_application(application_id: int, db = Depends(get_db)):
    """获取特定贷款申请详情"""
    try:
        application = next((app for app in mock_loan_applications if app["id"] == application_id), None)
        if not application:
            raise HTTPException(status_code=404, detail="贷款申请不存在")
        
        # 获取产品名称
        product = next((p for p in mock_loan_products if p["id"] == application["product_id"]), None)
        
        logger.info(f"📊 获取贷款申请详情: {application_id}")
        
        return LoanApplicationResponse(
            id=application["id"],
            application_number=application["application_number"],
            product_name=product["name"] if product else "未知产品",
            requested_amount=application["requested_amount"],
            requested_term_months=application["requested_term_months"],
            status=application["status"],
            submitted_at=datetime.fromisoformat(application["submitted_at"]),
            approved_amount=application.get("approved_amount"),
            approved_interest_rate=application.get("approved_interest_rate")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取贷款申请详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取贷款申请详情失败")