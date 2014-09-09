from ..migrator import upgrade_step


@upgrade_step('target', '', '2')
def target_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        value['status'] = value['status'].lower()


@upgrade_step('target', '2', '3')
def target_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1424

    tag_targets = [
        '59c3efe9-00c6-4b1b-858b-5a208478972c',
        'f2d60a72-7b9c-422a-a80e-9493640c1d58',
        '77d56f5a-e445-4f2c-83ac-65e00ce50ac1',
        '8a4e81d-3181-4332-9138-ecc39be4a3ab'
    ]

    nucleotide_targets = [
        '6f871a78-43a2-47fd-9b5d-7bbf086ba2ed',
        '0c988fd8-ee0e-46a9-8b7f-292ebbb27f05'
    ]

    other_targets = [
        'b5be1d51-88bb-4deb-811d-4b82627e39fb',
        'e45395d8-292a-4156-a85c-dfb81260c0fd',
        '2a33a354-b8dd-4c78-954a-b2962bacf799'
    ]

    ambiguous_targets = [
        'a1534246-56d0-4428-b71c-d54ee2899c8e',
        '14c70301-3751-4f4c-a7ce-c84ccc555edd',
        '455124cc-ee69-4ff7-bb5c-41d433b72e17',
        '077519e3-5b82-4a31-a5cf-719338cd8ce7'
    ]

    control_targets = [
        '89839f28-ad35-4bb4-a214-ee65d0a97d8d',
        '1ce5eb53-1441-4c0a-a095-1adc75c03f03',
        '2d3d0044-8e66-49d0-972b-6967ead8fca9',
        '87c25410-2ece-4335-b45b-eff245bb30bf',
        'a2e5a344-80ba-4def-84ac-ea0266d4a6e3',
        '77820475-506c-4b1a-bb2b-45e2113ad2ae',
        '6fcd4ef8-9a84-4951-958a-828c41a5ffb0',
        '2e19e501-8f32-4205-8469-2fb593a30595',
        '474ac43a-17d1-4aa7-a355-ddf95017fd86',
        '88195e80-70ba-4c23-ad58-2c1cdbf75fc0',
        '39af2e49-16cf-4fb6-9f64-c09743618186',
        '90db845c-432a-4d7f-b609-fc6d77366093',
        'd71a3b51-0651-41cb-9e4f-935cdd6c39ee',
        '94f6c959-1421-425a-ab81-d6e9d3c80051',
        '7bb8ba4a-6d1f-45a7-be66-632056bf9e68',
        '13360857-4ae8-43b3-a53a-fa0df37e608b',
        'efbd2716-2295-47b6-a52c-724a48e13095'
    ]

    recombinant_targets = [
        'HA',
        'YFP',
        '3XFLAG',
        'eGFP'
    ]

    histone_targets = [
        '452c5ea6-5880-499d-b8bb-392790fd2b89',
        'faf69adc-b03a-4128-a38e-930f2d8bea98',
        'e59f178d-1363-429e-9215-0db98882b993',
        '039b2e72-22bd-4868-bd57-a2c18c835f9e',
        '54618d10-b170-4ed0-905b-f013555ec5b1',
        '10ee2e0b-959e-457d-aff7-e45667cc254f',
        'b82f7e80-80a1-4aea-a8dc-bee540afc95a',
        '8ab82bd5-edb5-4fef-9ce1-26d557eda77c',
        '9b1f4911-e9ff-486e-963e-9f036e675fa5',
        '466a8840-38b7-42ea-a8e3-d06ea9ba9900',
        '9f870013-a8f7-4dc2-a547-22961b69bfea',
        'ee8091d5-3d70-48fe-bd76-9bc1450f29e0',
        'c8bb8de3-80e8-4f76-adc4-1db0a61bf6ba',
        '1e7d2f20-5db6-40cc-ab95-e44972f13608',
        'b01c1309-c1d4-487a-95b3-c2c8bb14952e',
        '1050238d-fc5a-4778-9046-5105157ec86e',
        '1ea12c3c-8b6a-4950-91a9-6a2b217b3e48',
        '9149aeb2-b747-4ff4-812c-7d96cda1d1cf',
        'a36a6041-f503-46ed-9310-db544aa6a26c',
        'a2cd45c9-f214-4af8-9051-87afc828c987',
        '6d25d67e-6ba3-4150-ad46-98b77ebce946',
        '08fcd376-0f9e-4623-8333-7cc25ced59bc',
        '9e6c7ada-61ef-49e2-b7d5-c59733e67e7b',
        'a0b96e89-f963-4a39-830a-3d016295cc79',
        '4ec56b6f-f0fb-4fda-9367-507a16fbf906',
        'f22be0d6-5a52-43a9-87ad-54c66173f365',
        '9fdbd27b-4118-4851-b566-87d77d467d79',
        'a1b236fc-38d5-4af5-a140-ede8bb6327c8',
        'd3fb07b7-75b9-426d-9a9f-61d32fec6ca3',
        '01bcac7b-2902-4153-b31b-a38f0e8f7211',
        '672fbd6d-9003-42c4-b88c-82e7daf178ef',
        '875453be-90cd-4da3-9b43-cd6933c8cff3',
        '84487b44-fb6c-46c5-a0b1-293b80545d94',
        'b7f85e20-3114-4d84-a9af-ea77c07ff102',
        'dbb12a8a-b240-44d0-839b-5ff39c552d7d',
        'afa96b1d-2b6a-40b6-9be3-a93d6715f846',
        'eade499f-c1da-41b2-abc3-f39baab2ee72',
        '86108f5d-fe24-4e4a-a259-de6e86184d40',
        'a19652bb-2f93-42fe-9d79-8903b8c97143',
        '1e90ac9a-4619-4e7a-b45f-5d9c93126292',
        'f8aaec94-788a-4be1-b14c-0ef28a8962fd',
        '5e51137f-71b2-49d9-87ce-a4a68074099e',
        '1aa5391a-01f1-4983-bdb6-d93db5f53334',
        'f24f7c5e-ff07-4a8d-8f7d-695667606ce3',
        'ccdae63a-7d7d-4283-9c69-ed0e92d04d2f',
        '3f449c7d-bd70-481c-8893-55981b2cddd3',
        '22d70759-9f8e-448b-8ce1-34b46840a8aa',
        'a47092ec-35ab-447c-aae3-c59c621cf094',
        '65b74663-aedd-46ae-b2c5-f3e37c834867',
        '3730e221-5625-4ce1-87b7-1e5bee47ae53',
        'eb576cba-6071-4c28-bba6-3c16fdbce0c7',
        '6847d42d-f2f2-4316-9df4-12f511fe35e7',
        'd3572908-87d8-42e3-954e-5a4277d700bb',
        '39131b65-b453-4246-a828-909e1de04698',
        '0c0d47a5-28a6-424f-b0c8-80c89dff2765',
        '6efda346-c51b-45b8-af51-760bbebb393e',
        '74470614-b3a5-4bfc-871a-32b9dc55bb1b',
        'bc472e4a-2ad3-483e-b059-391d150c0bff',
        '4af047f2-cd06-4758-8446-27297de01e28',
        '7a3b3aab-fb03-4274-9dfd-bcea06172f43',
        'e15b89d6-5a8f-41af-bfeb-b4affa5f472c',
        '761296be-a6c4-43be-b702-221401e5cce5',
        '4137e028-fbcf-4334-8c87-f3d921b68a8e',
        'fc83db34-5810-4297-af82-b56cc0ef2521',
        'c115e37b-f6b2-4a22-9a9d-21e32e4e2605',
        '851ee528-4763-4dba-9191-7db1ef7566f7',
        '9783fa7d-80eb-4dcf-b6d8-aee5189217e1',
        '1644b703-2835-44cd-93ec-bc514edaf84d',
        '0f586bec-e356-4e74-8d3b-39feb7e6d2d5',
        '47278add-f254-4cb6-9b36-026aeca04802',
        'dc2a9b76-823d-496f-8516-f00e270ec8e5',
        'd1dc9300-c6bc-48ea-81a1-df7823111176',
        '84e39ae9-5755-4987-963e-0551dd4da885',
        '1b4e458f-15ed-40c3-9dd1-1d6ae332f882',
        'f1e8ebfa-f3f0-4b04-bf88-a35df13a7eee',
        '14173a5f-799e-4dae-b155-a142c5b6b566',
        '49dd07ea-5b55-414c-bab0-b117b586f85a',
        'bf144aa3-2918-4c53-a059-829e5187feea',
        '32048733-94ec-46fa-a1ae-02f5f5214991',
        '3fb92833-8f90-4c74-87b1-ef8a70837761',
        '978de56c-33d3-497f-9102-a0b4d8a4030e',
        'e7a546d3-eaa1-49f7-956d-58019fcabba2',
        'f74ee061-611b-4571-bf2e-20c81be7ed0f',
        '243ce169-ab12-4229-9856-a55ce0b3b45a',
        '3600089e-fcad-49b1-87fb-28150bd15e59',
        '5dcb5fff-0141-4072-9122-3e281577d069',
        '202c2c52-46c1-4f8d-b4d3-9c175ec22df4',
        '7ab5ce93-340b-49b4-bf29-dc1f15c87cd5',
        'f93f67d9-a3bd-455a-9304-e59ae3cb917a',
        'a340a617-4ad4-481b-b409-91e38d046c63',
        '8eea4549-89ca-450f-adff-e1e1ae293571',
        'a2d65c6c-8f10-498d-85fe-9f16653b0cdc',
        '8054256a-ac89-485e-88a1-e7ed39595dd8',
        '4de86f6b-fb50-4cfd-ae65-0e795d7b708e',
        'e8659875-43dd-4a4c-85dd-3bbf2666a91c',
        '62b645a4-c150-4eb9-8294-83e6665ba196'
    ]

    tag_prefix = value['label'].split('-')[0]

    if value['uuid'] in tag_targets:
        value['investigated_as'] = ['tag']
    elif value['uuid'] in nucleotide_targets:
        value['investigated_as'] = ['nucleotide modification']
    elif value['uuid'] in other_targets:
        value['investigated_as'] = ['other context']
    elif value['uuid'] in ambiguous_targets:
        value['investigated_as'] = ['other context', 'transcription factor']
    elif value['uuid'] in control_targets:
        value['investigated_as'] = ['control']
    elif tag_prefix in recombinant_targets:
        value['investigated_as'] = ['recombinant protein', 'transcription factor']
    elif value['uuid'] in histone_targets:
        value['investigated_as'] = ['histone modification']
    else:
        value['investigated_as'] = ['transcription factor']
