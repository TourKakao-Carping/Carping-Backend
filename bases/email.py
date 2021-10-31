from django.core.mail import message
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string


EMAIL_REJECTED_REASON = {
    0: "회원님의 유료 포스트가 등록이 완료되었으니 확인 부탁드립니다. 감사합니다.",
    1: "고객 정보 불일치\n\n고객님의 앱 내 등록 정보와 금융 정보가 불일치합니다.\n계좌 번호, 은행, 실명 확인 부탁드립니다.\n정보 수정 후에 포스트 등록하시면 내부 검토를 재진행 하겠습니다.",
    2: "포스트 신뢰도 미충족\n\n유료 포스트는 판매자에게 저작권에 대한 책임과 권리가 있으며, 본인에게 저작권이 있는 자료만 등록하셔야 합니다.\n다만, 내부 검토 결과 해당 포스트는 포스트 저작권 문제, 타 포스트와 중복 문제 등으로 인한 내부 신뢰도 조건이 충족되지 않습니다.\n포스트 수정 후, 포스트 등록하시면 내부 검토를 재진행하겠습니다.",
    3: "포스트 가격 조건 미충족\n\n해당 포스트는 과도하게 높거나 낮은 가격 책정으로 인해 플랫폼의 취지와 맞지 않기에 포스트 수정을 요청합니다.\n카핑은 차박의 가치 제고를 위해 정보를 공유하는 플랫폼입니다. 플랫폼 질서를 위해 최소한의 가격 조건을 적용하고 있으니 양해 부탁드립니다.\n포스트 가격 조건 수정 후, 포스트 등록하시면 내부 검토를 재진행하겠습니다.",
    4: "포스트 내용 및 이미지 누락\n\n해당 포스트는 파일의 오류 및 내용의 일치성, 파일내 내용 및 이미지 누락 등의 문제가 존재합니다.\n포스트 내 사진의 형식과 파일의 형태 등을 확인 하신 후에, 포스트 등록 요청 드립니다.\n포스트 내용 수정 후, 포스트 등록하시면 내부 검토를 재진행하겠습니다.\n",
    5: "기타\n\n해당 포스트는 내부 검토 결과, 카핑의 유료포스트 조건에 충족하지 않아 포스트 등록이 반려되었습니다..\n세부적인 반려 사유는 추후 메일로 전달하겠습니다.\n반려 사유 송부 전, 포스트 수정 후에 포스트를 등록하시면 내부검토를 재진행하겠습니다."
}


def send_email(is_rejected, type, author, post_title, post_category):
    subject = "[카핑] 유료포스트 "
    message = "안녕하세요 카핑입니다.\n저희 유료포스트를 이용해 주셔서 감사드립니다. 유료포스트 등록 관련하여 안내 드립니다.\n"
    if is_rejected:
        subject += "등록 완료 안내"
        message = "회원님의 유료 포스트가 등록이 완료되었으니 확인 부탁드립니다. 감사합니다."
    else:
        subject += "신청 부적합 안내"
        message = "아래와 같은 사유로 신청이 반려되었으니\n확인 부탁드리며, 재요청 해주시면 감사하겠습니다.\n\n\n\n"

    detail_messagee = EMAIL_REJECTED_REASON[type]

    message = render_to_string('email/post_result_notification.html', {
        'author': author,
        'detail_message': detail_messagee,
        'is_rejected': is_rejected,
        'post_title': post_title,
        'post_category': post_category
    })
    to = [author.email]

    email = EmailMessage(subject=subject, body=message, to=to)
    email.content_subtype = "html"

    email.send()
