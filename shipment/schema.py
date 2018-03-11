import graphene
from shipment.shipment_calculator import shipment_calculator


class ShipmentRequest(graphene.InputObjectType):
    id = graphene.String(required=True)
    quantity = graphene.Int(required=True)


class ShipmentResult(graphene.ObjectType):
    amount = graphene.Float()


class QueryShipment(graphene.ObjectType):

    shipmentCalculator = graphene.Field(
        ShipmentResult, cart=graphene.List(ShipmentRequest))

    def resolve_shipmentCalculator(self, info, cart):
        data = []
        for item in cart:
            data.append({
                'code': item.id,
                'quantity': item.quantity
            })
        result = ShipmentResult()
        result.amount = shipment_calculator.calculate(data)
        return result


shipment_calculator
