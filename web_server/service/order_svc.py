from collections import defaultdict
from typing import Dict

from django.db.models import Count

from web_server.service.models import DosimetryAnalysisBase as analysis


class OrderInfos:
    def __init__(self, order) -> None:
        self.order = order
        self.queryset_func = self._one_to_many_function()

    def _one_to_many_function(self):
        if self.order.service_name == self.order.ServicesName.CLINIC_DOSIMETRY.value:
            queryset_func = self.order.clinic_dosimetry_analysis
        elif self.order.service_name == self.order.ServicesName.PRECLINIC_DOSIMETRY.value:
            queryset_func = self.order.preclinic_dosimetry_analysis
        elif self.order.service_name == self.order.ServicesName.SEGMENTANTION_QUANTIFICATION.value:
            queryset_func = self.order.segmentation_analysis
        elif self.order.service_name == self.order.ServicesName.RADIOSYNOVIORTHESIS.value:
            queryset_func = self.order.radiosyno_analysis

        return queryset_func

    @property
    def analysis_concluded(self) -> int:
        return self.queryset_func.filter(status=analysis.Status.CONCLUDED).count()

    @property
    def analysis_processing(self) -> int:
        return self.queryset_func.filter(status=analysis.Status.PROCESSING).count()

    @property
    def analysis_analyzing_infos(self) -> int:
        return self.queryset_func.filter(status=analysis.Status.ANALYZING_INFOS).count()

    @property
    def analysis_data_sent(self) -> int:
        return self.queryset_func.filter(status=analysis.Status.DATA_SENT).count()

    @property
    def analysis_invalid_infos(self) -> int:
        return self.queryset_func.filter(status=analysis.Status.INVALID_INFOS).count()

    def _analysis_status_count(self) -> Dict:
        """
        Slow version: Multiple queries on db
        """
        return dict(
            data_set=self.analysis_data_sent,
            invalid_infos=self.analysis_invalid_infos,
            concluded=self.analysis_concluded,
            processing=self.analysis_processing,
            analyzing_infos=self.analysis_analyzing_infos,
        )

    def analysis_status_count(self) -> Dict:

        sum_by_status = self.queryset_func.values('status').annotate(count=Count('status'))

        counts = defaultdict(int)
        for item in sum_by_status:
            counts[item['status']] = item['count']

        return dict(
            data_set=counts['DS'],
            invalid_infos=counts['II'],
            concluded=counts['CO'],
            processing=counts['PR'],
            analyzing_infos=counts['AI'],
        )

    def are_analyzes_available(self):
        return self.order.remaining_of_analyzes > 0

    def has_payment_confirmed(self):
        return self.order.status_payment == self.order.PaymentStatus.CONFIRMED


def order_to_dict(order, request):

    analysis_infos = OrderInfos(order).analysis_status_count()

    dict_ = {
        'id': order.uuid,
        'user_id': order.user.uuid,
        'quantity_of_analyzes': order.quantity_of_analyzes,
        'remaining_of_analyzes': order.remaining_of_analyzes,
        'price': order.price,
        'service_name': order.get_service_name_display(),
        'status_payment': order.get_status_payment_display(),
        'active': order.active,
        'analysis_status': analysis_infos,
        'code': order.code,
        'created_at': order.created_at.date(),
    }

    if order.payment_slip.name:
        dict_['payment_slip_url'] = request.build_absolute_uri(order.payment_slip.url)
    else:
        dict_['payment_slip_url'] = None

    return dict_
