from typing import Dict

from web_server.service.models import DosimetryAnalysisBase as analysis


class OrderInfos:
    def __init__(self, order) -> None:
        self.order = order
        self.queryset_func = self._one_to_many_function()

    def _one_to_many_function(self):
        if self.order.service_name == self.order.CLINIC_DOSIMETRY:
            queryset_func = self.order.clinic_dosimetry_analysis
        elif self.order.service_name == self.order.PRECLINIC_DOSIMETRY:
            queryset_func = self.order.preclinic_dosimetry_analysis
        elif self.order.service_name == self.order.SEGMENTANTION_QUANTIFICATION:
            queryset_func = self.order.segmentation_analysis

        return queryset_func

    @property
    def analysis_concluded(self) -> int:
        return self.queryset_func.filter(status=analysis.CONCLUDED).count()

    @property
    def analysis_processing(self) -> int:
        return self.queryset_func.filter(status=analysis.PROCESSING).count()

    @property
    def analysis_analyzing_infos(self) -> int:
        return self.queryset_func.filter(status=analysis.ANALYZING_INFOS).count()

    def analysis_status_count(self) -> Dict:
        # TODO: add INVALID_INFOS
        return dict(
            concluded=self.analysis_concluded,
            processing=self.analysis_processing,
            analyzing_infos=self.analysis_analyzing_infos,
        )


def order_to_dict(order):

    analysis_infos = OrderInfos(order).analysis_status_count()
    return {
        'id': order.uuid,
        'user_id': order.user.uuid,
        'quantity_of_analyzes': order.quantity_of_analyzes,
        'remaining_of_analyzes': order.remaining_of_analyzes,
        'price': order.price,
        'service_name': order.get_service_name_display(),
        'status_payment': order.get_status_payment_display(),
        'permission': order.permission,
        'created_at': order.created_at.date(),
        'analysis_status': analysis_infos,
        'code': order.code,
    }
