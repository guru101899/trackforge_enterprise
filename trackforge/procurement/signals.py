from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import PurchaseOrder
from inventory.models import Stock, StockTransaction


@receiver(post_save, sender=PurchaseOrder)
def update_purchase_order_on_status_choices(sender, created, instance, **kwargs):
    def run_stock_update():
        # 1. Skip if still in planning stages
        if instance.status in ["draft", "submitted"]:
            return

        # 2. STATUS: COMPLETED
        elif instance.status == "completed":
            already_completed = StockTransaction.objects.filter(
                reference_document=f"PO: {instance.reference_number}",
                transaction_type="po_complete"
            ).exists()

            if already_completed:
                return

            for item in instance.items.all():
                # Gap Math: Total ordered minus what was already received as 'partial'
                partial_history = StockTransaction.objects.filter(
                    reference_document=f"PO: {instance.reference_number}",
                    stock__product=item.product,
                    transaction_type="po_partial"
                ).aggregate(total=Sum("quantity_changed"))['total'] or 0

                remaining_to_add = item.quantity - partial_history

                if remaining_to_add > 0:
                    stock, _ = Stock.objects.get_or_create(
                        product=item.product,
                        warehouse=instance.warehouse,
                        defaults={"quantity": 0}
                    )
                    stock.quantity += remaining_to_add
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_complete",
                        quantity_changed=remaining_to_add,
                        stock_after_transaction=stock.quantity,
                        reference_document=f"PO: {instance.reference_number}"
                    )

        # 3. STATUS: PARTIAL (Wave-based delivery)
        elif instance.status == "partial":
            for item in instance.items.all():
                # Gap Math: What's on screen minus what we already logged for this product
                history = StockTransaction.objects.filter(
                    reference_document=f"PO: {instance.reference_number}",
                    stock__product=item.product,
                    transaction_type="po_partial",
                ).aggregate(total=Sum("quantity_changed"))['total'] or 0

                amount_to_add = item.quantity_received - history

                if amount_to_add > 0:
                    stock, _ = Stock.objects.get_or_create(
                        product=item.product,
                        warehouse=instance.warehouse,
                        defaults={"quantity": 0}
                    )
                    stock.quantity += amount_to_add
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_partial",
                        quantity_changed=amount_to_add,
                        stock_after_transaction=stock.quantity,
                        reference_document=f"PO: {instance.reference_number}"
                    )

        # 4. STATUS: CANCELLED (Undo all additions)
        elif instance.status == "cancelled":
            for item in instance.items.all():
                history_to_undo = StockTransaction.objects.filter(
                    reference_document=f"PO: {instance.reference_number}",
                    stock__product=item.product,
                    transaction_type__in=["po_complete", "po_partial"]
                ).aggregate(total=Sum("quantity_changed"))['total'] or 0

                if history_to_undo > 0:
                    stock = Stock.objects.get(product=item.product, warehouse=instance.warehouse)
                    stock.quantity -= history_to_undo
                    stock.save()

                    StockTransaction.objects.create(
                        stock=stock,
                        transaction_type="po_cancel",
                        quantity_changed=history_to_undo,
                        stock_after_transaction=stock.quantity,
                        reference_document=f"PO: {instance.reference_number}"
                    )

    # Use on_commit to ensure POLineItems are saved before the logic runs
    transaction.on_commit(run_stock_update)