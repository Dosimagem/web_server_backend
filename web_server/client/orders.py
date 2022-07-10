from web_server.service.models import (ComputationalModelOrder,
                                       DosimetryOrder,
                                       SegmentationOrder)


class Orders:

    def __init__(self, user):
        self.user = user

    def clinical_dosimetry_orders(self):
        return list(DosimetryOrder.objects.filter(requester=self.user, type=DosimetryOrder.CLINICAL))

    def preclinical_dosimetry_orders(self):
        return list(DosimetryOrder.objects.filter(requester=self.user, type=DosimetryOrder.PRECLINICAL))

    def segmentation_orders(self):
        return list(SegmentationOrder.objects.filter(requester=self.user))

    def computation_orders(self):
        return list(ComputationalModelOrder.objects.filter(requester=self.user))

    def all_orders(self):
        d = list(DosimetryOrder.objects.filter(requester=self.user))
        s = self.segmentation_orders()
        c = self.computation_orders()
        return d + s + c
