#ifndef __lib_dvb_subtitle_h
#define __lib_dvb_subtitle_h

#include <lib/base/object.h>
#include <lib/dvb/idvb.h>
#include <lib/dvb/pesparse.h>
#include <lib/gdi/gpixmap.h>

typedef unsigned char __u8;

struct subtitle_clut_entry
{
	__u8 Y, Cr, Cb, T;
	__u8 valid;
};

struct subtitle_clut
{
	unsigned char clut_id;
	unsigned char CLUT_version_number;
	subtitle_clut_entry entries_2bit[4];
	subtitle_clut_entry entries_4bit[16];
	subtitle_clut_entry entries_8bit[256];
	subtitle_clut *next;
};

struct subtitle_page_region
{
	int region_id;
	int region_horizontal_address;
	int region_vertical_address;
	subtitle_page_region *next;
};

struct subtitle_region_object
{
	int object_id;
	int object_type;
	int object_provider_flag;
	
	int object_horizontal_position;
	int object_vertical_position;
	
		// not supported right now...
	int foreground_pixel_value;
	int background_pixel_value;

	subtitle_region_object *next;
};

struct subtitle_region
{
	int region_id;
	int region_version_number;
	int region_height, region_width;
	enum depth { bpp2=1, bpp4=2, bpp8=3 } region_depth;
	
	ePtr<gPixmap> region_buffer;
	
	int clut_id;
	
	subtitle_region_object *region_objects;
	
	subtitle_region *next;
	
	bool committed;
};

struct subtitle_page
{
	int page_id;
	time_t page_time_out;
	int page_version_number;
	int state;
	int pcs_size;
	subtitle_page_region *page_regions;
	
	subtitle_region *regions;

	subtitle_clut *cluts;

	subtitle_page *next;
};

struct bitstream
{
	__u8 *data;
	int size;
	int avail;
	int consumed;
};

struct eDVBSubtitleRegion
{
	ePtr<gPixmap> m_pixmap;
	ePoint m_position;
	eDVBSubtitleRegion &operator=(const eDVBSubtitleRegion &s)
	{
		m_pixmap = s.m_pixmap;
		m_position = s.m_position;
		return *this;
	}
};

struct eDVBSubtitlePage
{
	std::list<eDVBSubtitleRegion> m_regions;
	pts_t m_show_time;
};

class eDVBSubtitleParser
	:public iObject, public ePESParser, public Object
{
	DECLARE_REF(eDVBSubtitleParser);
	subtitle_page *m_pages;
	ePtr<iDVBPESReader> m_pes_reader;
	ePtr<eConnection> m_read_connection;
	pts_t m_show_time;
	Signal1<void,const eDVBSubtitlePage&> m_new_subtitle_page;
	int m_composition_page_id, m_ancillary_page_id;
public:
	eDVBSubtitleParser(iDVBDemux *demux);
	virtual ~eDVBSubtitleParser();
	int start(int pid, int composition_page_id, int ancillary_page_id);
	int stop();
	void connectNewPage(const Slot1<void, const eDVBSubtitlePage&> &slot, ePtr<eConnection> &connection);
private:
	void subtitle_process_line(subtitle_page *page, int object_id, int line, __u8 *data, int len);
	int subtitle_process_pixel_data(subtitle_page *page, int object_id, int *linenr, int *linep, __u8 *data);
	int subtitle_process_segment(__u8 *segment);
	void subtitle_process_pes(__u8 *buffer, int len);
	void subtitle_redraw_all();
	void subtitle_reset();
	void subtitle_redraw(int page_id);
	void processPESPacket(__u8 *pkt, int len) { subtitle_process_pes(pkt, len); }
};

#endif