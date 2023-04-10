ster='select [OrderNumber],[Name],[Email],[GiftCycleId],[DeliveryURL],[ShippingDate] from [dbo].[Order] LEFT JOIN [dbo].[Recipient]ON [dbo].[Order].RecipientId = [dbo].[Recipient].RecipientId where OrderNumber is not null and [GiftCycleId]=?'
sml=ster[:-19]
print(sml)