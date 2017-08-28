import { unreleasedFilesUrl } from '../globals';


describe('Global utility functionality', () => {
    test('unreleasedFilesUrl not logged in functions properly', () => {
        const context = {
            '@id': '/experiments/ENCSR000AAA',
        };

        // First test basic statuses -- those without additions nor subtractions.
        const basicStatuses = unreleasedFilesUrl(context);
        expect(basicStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=in%20progress&status=released&status=archived`);

        // Test basic statuses plus additions.
        let testStatuses = unreleasedFilesUrl(context, false, { addStatuses: ['upload failed', 'replaced'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=in%20progress&status=released&status=archived&status=upload%20failed&status=replaced`);

        // Test basic statuses with subtractions.
        testStatuses = unreleasedFilesUrl(context, false, { subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=in%20progress&status=archived`);

        // Test basic statuses with with both additions and subtractions.
        testStatuses = unreleasedFilesUrl(context, false, { addStatuses: ['upload failed', 'replaced'], subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=in%20progress&status=archived&status=upload%20failed&status=replaced`);
    });

    test('unreleasedFilesUrl logged in functions properly', () => {
        const context = {
            '@id': '/experiments/ENCSR000AAA',
        };

        // First test basic statuses -- those without additions nor subtractions.
        const basicStatuses = unreleasedFilesUrl(context, true);
        expect(basicStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=upload%20failed&status=in%20progress&status=deleted&status=released&status=replaced&status=revoked&status=archived`);

        // Test basic statuses plus additions.
        let testStatuses = unreleasedFilesUrl(context, true, { addStatuses: ['upload failed', 'replaced'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=upload%20failed&status=in%20progress&status=deleted&status=released&status=replaced&status=revoked&status=archived`);

        // Test basic statuses with subtractions.
        testStatuses = unreleasedFilesUrl(context, true, { subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=upload%20failed&status=in%20progress&status=deleted&status=replaced&status=revoked&status=archived`);

        // Test basic statuses with with both additions and subtractions.
        testStatuses = unreleasedFilesUrl(context, true, { addStatuses: ['upload failed', 'replaced'], subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=upload%20failed&status=in%20progress&status=deleted&status=replaced&status=revoked&status=archived`);
    });
});
