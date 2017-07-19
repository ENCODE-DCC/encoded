import { unreleasedFilesUrl } from '../globals';


describe('Global utility functionality', () => {
    test('unreleasedFilesUrl functions properly', () => {
        const context = {
            '@id': '/experiments/ENCSR000AAA',
        };

        // First test basic statuses -- those without additions nor subtractions.
        const basicStatuses = unreleasedFilesUrl(context);
        expect(basicStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=in%20progress&status=released&status=archived`);

        // Test basic statuses plus additions.
        let testStatuses = unreleasedFilesUrl(context, { addStatuses: ['upload failed', 'replaced'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=content%20error&status=in%20progress&status=released&status=archived&status=upload%20failed&status=replaced`);

        // Test basic statuses with subtractions.
        testStatuses = unreleasedFilesUrl(context, { subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=in%20progress&status=archived`);

        // Test basic statuses with with both additions and subtractions.
        testStatuses = unreleasedFilesUrl(context, { addStatuses: ['upload failed', 'replaced'], subtractStatuses: ['content error', 'released'] });
        expect(testStatuses).toEqual(`/search/?limit=all&type=File&dataset=${context['@id']}&status=uploading&status=in%20progress&status=archived&status=upload%20failed&status=replaced`);
    });
});
