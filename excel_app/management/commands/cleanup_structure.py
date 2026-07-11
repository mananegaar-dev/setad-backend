import re

from django.core.management.base import BaseCommand
from django.db import transaction

from excel_app.models import Area, BoardOfTrustee, Fields, Neighborhood, SubArea


class Command(BaseCommand):
    help = "Normalize names and merge duplicated Area/SubArea/Neighborhood/BoardOfTrustee records"

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return ""
        text = str(value).replace("\u200c", " ").strip()
        return re.sub(r"\s+", " ", text)

    def _merge_areas(self):
        keepers = {}
        merged = 0
        for area in Area.objects.all().order_by("id"):
            norm = self._normalize_text(area.name)
            if not norm:
                continue
            if norm in keepers:
                keeper = keepers[norm]
                SubArea.objects.filter(area=area).update(area=keeper)
                area.delete()
                merged += 1
                continue
            if area.name != norm:
                area.name = norm
                area.save(update_fields=["name"])
            keepers[norm] = area
        return merged

    def _merge_sub_areas(self):
        keepers = {}
        merged = 0
        for sub in SubArea.objects.all().order_by("id"):
            norm = self._normalize_text(sub.name)
            if not norm:
                continue
            key = (sub.area_id, norm)

            if key in keepers:
                keeper = keepers[key]

                for neighborhood in Neighborhood.objects.filter(sub_area=sub).order_by("id"):
                    n_name = self._normalize_text(neighborhood.name)
                    target = Neighborhood.objects.filter(sub_area=keeper, name=n_name).first()
                    if target:
                        Fields.objects.filter(neighborhood=neighborhood).update(neighborhood=target, sub_area=keeper)
                        neighborhood.delete()
                    else:
                        if neighborhood.name != n_name:
                            neighborhood.name = n_name
                            neighborhood.save(update_fields=["name"])
                        neighborhood.sub_area = keeper
                        neighborhood.save(update_fields=["sub_area"])

                Fields.objects.filter(sub_area=sub, neighborhood__isnull=True).update(sub_area=keeper)
                sub.delete()
                merged += 1
                continue

            if sub.name != norm:
                sub.name = norm
                sub.save(update_fields=["name"])
            keepers[key] = sub

        return merged

    def _merge_neighborhoods(self):
        merged = 0
        for sub in SubArea.objects.all():
            keepers = {}
            for neighborhood in Neighborhood.objects.filter(sub_area=sub).order_by("id"):
                norm = self._normalize_text(neighborhood.name)
                if not norm:
                    continue
                key = (sub.id, norm)
                if key in keepers:
                    keeper = keepers[key]
                    Fields.objects.filter(neighborhood=neighborhood).update(neighborhood=keeper)
                    neighborhood.delete()
                    merged += 1
                    continue
                if neighborhood.name != norm:
                    neighborhood.name = norm
                    neighborhood.save(update_fields=["name"])
                keepers[key] = neighborhood
        return merged

    def _merge_board_members(self):
        keepers = {}
        merged = 0
        for board in BoardOfTrustee.objects.all().order_by("id"):
            norm = self._normalize_text(board.name)
            if not norm:
                Fields.objects.filter(board_of_trustees=board).update(board_of_trustees=None)
                board.delete()
                merged += 1
                continue
            if norm in keepers:
                keeper = keepers[norm]
                Fields.objects.filter(board_of_trustees=board).update(board_of_trustees=keeper)
                board.delete()
                merged += 1
                continue
            if board.name != norm:
                board.name = norm
                board.save(update_fields=["name"])
            keepers[norm] = board
        return merged

    def handle(self, *args, **options):
        with transaction.atomic():
            area_merged = self._merge_areas()
            sub_merged = self._merge_sub_areas()
            neighborhood_merged = self._merge_neighborhoods()
            board_merged = self._merge_board_members()

        board_count = BoardOfTrustee.objects.count()
        self.stdout.write(self.style.SUCCESS("Cleanup completed."))
        self.stdout.write(f"Merged areas: {area_merged}")
        self.stdout.write(f"Merged sub areas: {sub_merged}")
        self.stdout.write(f"Merged neighborhoods: {neighborhood_merged}")
        self.stdout.write(f"Merged board members: {board_merged}")
        self.stdout.write(f"Current board catalog count: {board_count}")
        if board_count > 24:
            self.stdout.write(self.style.WARNING("Board catalog is still above 24 records. Please review and remove extras manually."))
